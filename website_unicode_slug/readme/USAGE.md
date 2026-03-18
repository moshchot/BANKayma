To use this module, you need to:

1. Fill in some non-ascii character in a blog title
2. Observe the slug generated will contain this character

Note that under the hood this will create urls with percent encoding, which look odd when looking at the raw url (most browsers show the unicode version though)
