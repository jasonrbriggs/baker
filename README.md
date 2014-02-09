sitebaker
=========

Sitebaker is a simple static site generator using Python and the [proton](https://github.com/jasonrbriggs/proton) template engine for templating, and [markdown](http://daringfireball.net/projects/markdown/‎) for content.

Quick Start
-----------

Install SiteBaker using the following command:

    pip install sitebaker

Create the skeleton of a new site by running the following:

    baker create mysite

A new directory (mysite) is created, containing a basic directory structure, templates, and a configuration file (site.ini).
Edit the site.ini to your requirements, and then run the generate command to test the process:

    cd mysite
    baker generate

Create a new blog entry, by running the blog command:

    baker blog "This is a test post title"

You'll find a new file (this-is-a-test-post-title.text) has been created in the directory: mysite/blog/yyyy/mm/dd/.
An RSS xml file has also been created, along with an index.html for the blog dir.
