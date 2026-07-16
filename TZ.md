# TZ.md

# Technical Specification (TZ)

## Project Overview

Develop a modern, responsive news portal using only:

* Django
* PostgreSQL
* HTML5
* CSS3
* Vanilla JavaScript (ES6)

The project must not use React, Vue, Angular, jQuery or any SPA framework.

The website language is Azerbaijani only.

The entire project must strictly follow the rules defined in **CLAUDE.md**.

---

# Website Structure

The public website must contain the following pages:

* Home
* Category
* Subcategory
* News Article
* Search
* Archive
* About
* Contact
* Privacy Policy
* Terms of Use
* 404
* 500

All pages must be responsive.

---

# Home Page

The homepage should include:

* Header
* Navigation
* Breaking News Ticker
* Featured News
* Latest News
* Category Sections
* Popular News
* Sidebar
* Advertisement Blocks
* Newsletter Block (optional)
* Footer

Content must be loaded dynamically from the database.

---

# Category System

The website must support a fixed category hierarchy.

Structure:

Category

↓

Subcategory

Only two levels are supported.

Example:

Politics

↓

International

Technology

↓

Artificial Intelligence

The navigation menu must display categories and subcategories using dropdown menus.

Category order is managed manually in the CMS.

---

# News

Every article must support:

* Title
* Slug
* Short Description
* Full Content
* Featured Image
* Gallery
* Category
* Subcategory
* Tags
* Author
* Publication Date
* Updated Date
* Reading Time
* View Counter
* Related Articles
* Featured Status
* Breaking News Status
* Draft
* Scheduled Publishing
* Published
* Archived

---

# Search

The website must provide a search page.

Search supports:

* Article Title
* Article Content
* Categories
* Tags

Search results should be paginated.

---

# Archive

Archive pages should allow browsing articles by:

* Year
* Month

---

# CMS

The project must include a fully custom CMS.

Do not use Django Admin as the administration interface.

CMS includes:

Dashboard

News Management

Categories

Tags

Media Library

Advertisements

Static Pages

SEO

Users

Settings

Activity Logs

---

# Dashboard

Dashboard should display:

* Total Articles
* Published Articles
* Draft Articles
* Scheduled Articles
* Categories
* Users
* Latest Activity
* Recent Articles
* Quick Actions

---

# News Management

Editors must be able to:

Create

Edit

Preview

Save Draft

Schedule

Publish

Archive

Delete

Duplicate

Restore

Bulk Actions

Every action must be logged.

---

# Rich Text Editor

Use CKEditor.

Toolbar should remain simple.

Enable only:

* Headings
* Bold
* Italic
* Underline
* Lists
* Links
* Tables
* Images
* Videos
* Quotes
* Alignment

---

# Media Library

Media library supports:

* Upload
* Preview
* Search
* Crop
* Replace
* Delete

Every uploaded image must automatically:

Validate

↓

Crop

↓

Optimize

↓

Convert to WebP

↓

Generate thumbnails

Only optimized images should be used on the website.

---

# Cropper

Every uploaded image must open in Cropper before saving.

Supported actions:

* Crop
* Zoom
* Rotate
* Reset
* Preview

---

# WebP

All uploaded JPEG and PNG images must automatically convert to WebP.

SVG files remain unchanged.

---

# SEO

Every article supports:

* Meta Title
* Meta Description
* Canonical URL
* Open Graph
* Structured Data
* Sitemap
* Robots
* Breadcrumbs

SEO should be generated automatically whenever possible.

---

# Advertisements

Support advertisement positions throughout the website.

Advertisements can be:

* Enabled
* Disabled
* Scheduled

Adding or removing advertisements must not require template modifications.

---

# Users

CMS must support roles:

* Administrator
* Editor-in-Chief
* Editor
* Journalist
* Content Manager

Permissions are role-based.

---

# Settings

CMS settings include:

* Website Name
* Logo
* Favicon
* Contact Information
* Social Links
* SMTP
* Analytics Code
* Maintenance Mode

---

# Responsive Design

The website must work correctly on:

Desktop

Laptop

Tablet

Mobile

Responsive behavior is mandatory.

---

# Performance

The project must use:

* PostgreSQL
* Redis
* Celery

Heavy tasks should execute in the background.

Images must be optimized.

Pages should load quickly.

---

# Security

The project must implement:

* Authentication
* Authorization
* CSRF Protection
* XSS Protection
* Secure File Upload
* Audit Logs

Every CMS action must be permission protected.

---

# Error Pages

Create custom pages for:

* 403
* 404
* 500

They must follow the same design language as the website.

---

# Development Requirements

The project must follow every rule defined in **CLAUDE.md**.

The codebase must be:

* Modular
* Readable
* Responsive
* Accessible
* Secure
* Optimized
* Scalable
* Production-ready

No demo-quality implementations are acceptable.

---

# Expected Result

The final result must be a fully functional commercial news portal with:

* Responsive public website
* Custom CMS
* Category/Subcategory system
* Professional news management
* CKEditor integration
* Image Cropper
* Automatic WebP conversion
* SEO optimization
* Fast performance
* Secure architecture
* Clean and maintainable code

The project should be ready for production deployment immediately after completion.
