from .i18n import localize_html, normalize_language


class SiteLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        language = normalize_language(request.session.get("site_language", "uk"))

        content_type = response.get("Content-Type", "")
        is_html = content_type.startswith("text/html")

        if language == "en" and is_html and not getattr(response, "streaming", False):
            charset = response.charset or "utf-8"
            html = response.content.decode(charset)
            localized_html = localize_html(html, language)

            if localized_html != html:
                response.content = localized_html.encode(charset)
                if response.has_header("Content-Length"):
                    response["Content-Length"] = str(len(response.content))

        return response
