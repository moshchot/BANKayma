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
        return super().blog_post(
            blog_post.blog_id,
            blog_post,
            tag_id=tag_id,
            page=page,
            enable_editor=enable_editor,
            **post
        )
