from odoo import http

from odoo.addons.website_blog.controllers import main as website_blog


class WebsiteBlog(website_blog.WebsiteBlog):
    @http.route(
        [
            '/news/<model("blog.post"):blog_post>',
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def blog_post(self, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        if http.request.env.user.has_group(
            "bankayma_website.group_website"
        ) and not http.request.env.user.has_group("website.group_website_designer"):
            # TODO
            pass
        return super().blog_post(
            blog_post.blog_id,
            blog_post,
            tag_id=tag_id,
            page=page,
            enable_editor=enable_editor,
            **post
        )

    @http.route(
        [
            "/news",
            "/news/page/<int:page>",
            "/news/tag/<string:tag>",
            "/news/tag/<string:tag>/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def news(self, blog=None, tag=None, page=1, search=None, **opt):
        result = self.blog(blog=blog, tag=tag, page=page, search=search, **opt)
        if hasattr(result, "qcontext") and result.qcontext.get("blog_url"):
            result.qcontext["blog_url"].path = "/news"
        return result
