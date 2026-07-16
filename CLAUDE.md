# CLAUDE.md

# Project Philosophy

## Purpose

This document defines the mandatory development standards for the News Portal project.

Every generated file, component, template and line of code must follow this document.

This document has higher priority than individual prompts unless the user explicitly changes a requirement.

The goal is not to generate code quickly.

The goal is to build a professional production-ready news platform.

Every architectural decision must prioritize:

* Maintainability
* Scalability
* Readability
* Security
* Performance
* Reusability

The project must look and behave like software developed by an experienced engineering team.

Never generate quick prototypes.

Never generate demo-quality code.

Never generate experimental architecture.

Generate production-quality code only.

---

# Development Principles

Always think before writing code.

Never start coding immediately.

First:

Analyze.

Design.

Plan.

Then implement.

Every new feature must fit into the existing architecture.

Never break architecture consistency.

---

# Code Philosophy

Every file should have one clear responsibility.

Avoid duplication.

Reuse existing components.

Follow the DRY principle.

Follow the SOLID principles whenever applicable.

Keep functions small.

Keep templates clean.

Keep CSS modular.

Keep JavaScript isolated.

Never sacrifice readability for shorter code.

Readable code is preferred over clever code.

---

# User Experience Philosophy

The user must always understand:

Where they are.

What they can do.

What happened.

What will happen next.

Interfaces must be intuitive.

Animations must never distract users.

Navigation must always remain predictable.

The website is a news portal.

Reading articles is the highest priority.

Everything else is secondary.

---

# Visual Philosophy

Minimalism.

Large white space.

Excellent typography.

Consistent spacing.

Clean hierarchy.

Professional appearance.

The design should remain relevant for many years.

Avoid trendy effects that become outdated quickly.

---

# CMS Philosophy

The CMS is a professional editorial workspace.

Editors spend many hours every day inside the CMS.

Therefore:

Speed is more important than decoration.

Clarity is more important than animation.

Consistency is more important than creativity.

Every action should require as few clicks as possible.

The interface should never confuse editors.

---

# Development Workflow

Every task follows this order:

1. Understand the requirement.

2. Analyze existing architecture.

3. Decide whether an existing component can be reused.

4. Implement the backend.

5. Implement templates.

6. Implement styling.

7. Implement JavaScript.

8. Test.

9. Optimize.

10. Document.

Never skip these steps.

---

# Long-Term Maintainability

The project should remain maintainable for at least ten years.

Future developers should immediately understand:

Project structure.

Naming conventions.

Templates.

Views.

Models.

CSS organization.

JavaScript organization.

No part of the project should depend on undocumented behavior.

Every important decision should be obvious from the code itself.

---

# Project Quality Standard

The expected quality level is equivalent to a commercial news platform developed by a professional software company.

Every generated solution must be production-ready.

No shortcuts.

No placeholder implementations.

No temporary fixes.

No unfinished code.

Every implementation should be complete, clean and maintainable.

This philosophy applies to every future task in this project.
# CLAUDE.md

# Chapter 2 — Project Goals

## Project Overview

The project is a modern news portal developed exclusively with Django, Django Templates, HTML5, CSS3 and Vanilla JavaScript.

The website is intended to be a professional online media platform capable of publishing news quickly, managing editorial workflows efficiently and scaling over time.

The project is **not** a blog.

The project is **not** a magazine template.

The project is a production-ready newsroom platform.

---

# Primary Goals

The project must achieve the following goals:

* Fast content publishing.
* Excellent reading experience.
* High performance.
* Professional editorial workflow.
* Clean architecture.
* Long-term maintainability.
* SEO optimization.
* Easy future expansion.

Every architectural decision should support these goals.

---

# Target Audience

The public website is intended for:

* Daily readers.
* Mobile users.
* Desktop users.
* Search engine visitors.
* Returning visitors.

The CMS is intended for:

* Administrators.
* Editors.
* Journalists.
* Content managers.

The CMS must never be designed for technical users only.

Every interface should be understandable without training.

---

# Business Objectives

The platform should be capable of supporting:

* Daily news publishing.
* Breaking news.
* Featured articles.
* Category-based content.
* Sponsored content.
* Advertisement placement.
* Long-term content archive.

Future monetization should be possible without redesigning the architecture.

---

# Scope

The first production version includes:

* Public news website.
* Custom CMS.
* Editorial workflow.
* Category hierarchy.
* Search.
* Tags.
* Static pages.
* Media management.
* SEO management.
* User management.
* Advertisement management.
* System settings.

Anything outside this list should be considered optional unless explicitly approved.

---

# Technologies

Backend:

* Python
* Django
* PostgreSQL
* Redis
* Celery

Frontend:

* Django Templates
* HTML5
* CSS3
* Vanilla JavaScript

Icons:

* Bootstrap Icons

Rich Text Editor:

* CKEditor

Image Processing:

* Cropper.js
* Pillow
* WebP conversion

No frontend frameworks are allowed.

Do not use:

* React
* Vue
* Angular
* Next.js
* Nuxt.js

---

# Language

The platform supports only one language.

Language:

Azerbaijani.

No multilingual architecture should be implemented.

Do not create translation models.

Do not implement i18n.

Do not implement language switchers.

---

# Public Website Goals

The public website must prioritize:

Fast loading.

Clear navigation.

Easy reading.

Strong typography.

Minimal distractions.

Responsive layout.

Accessibility.

SEO.

Every page should guide users naturally toward reading more articles.

---

# CMS Goals

The CMS must allow editors to perform daily work efficiently.

The CMS should reduce repetitive actions.

The CMS should minimize clicks.

The CMS should support large amounts of content without becoming difficult to use.

Every management screen should remain clean even when the database contains tens of thousands of records.

---

# Editorial Workflow

The platform should support the complete lifecycle of an article:

Draft

↓

Editing

↓

Review

↓

Scheduled Publication

↓

Published

↓

Archived

Every stage must be represented clearly in the CMS.

---

# Content Organization

Content should be organized using:

Categories

↓

Subcategories

↓

Articles

↓

Tags

The hierarchy must remain logical and easy to navigate.

Navigation menus should expose only the first two levels of categories.

---

# Performance Goals

Desktop Lighthouse Score target:

95+

Mobile Lighthouse Score target:

90+

Largest Contentful Paint (LCP):

Less than 2.5 seconds.

First Contentful Paint (FCP):

Less than 1.8 seconds.

Cumulative Layout Shift (CLS):

Below 0.1.

Time to Interactive:

As low as possible.

---

# Scalability Goals

The architecture should support future growth.

Examples:

* More categories.
* More users.
* More editors.
* Larger media library.
* Higher traffic.
* Additional modules.

No architectural decision should block future expansion.

---

# Maintainability Goals

The project should remain understandable after many years.

Future developers should be able to:

Understand the folder structure.

Understand naming conventions.

Locate components quickly.

Reuse existing modules.

Avoid unnecessary rewrites.

Every feature should have a clear place inside the architecture.

---

# Code Quality Goals

Generated code must be:

Readable.

Modular.

Reusable.

Documented where necessary.

Predictable.

Consistent.

Avoid overengineering.

Avoid premature optimization.

Avoid unnecessary abstraction.

---

# UI Goals

The interface should communicate trust.

The design should appear modern but timeless.

Whitespace should be used intentionally.

Typography should improve readability.

Every interactive element should provide clear visual feedback.

The UI should never overwhelm users.

---

# Final Goal

The finished product should feel like a commercial-quality news platform built by a professional software company.

Every future implementation should move the project closer to this goal.

If there is ever a conflict between speed of implementation and long-term quality, long-term quality must always take priority.
# CLAUDE.md

# Chapter 3 — Technology Stack & Development Standards

## General Technology Policy

This project must use a stable, maintainable and production-ready technology stack.

Every library, dependency and framework must have a clear purpose.

Do not install unnecessary packages.

Do not increase project complexity without measurable benefits.

Every dependency should improve maintainability, performance or developer productivity.

---

# Backend Stack

The backend must use:

* Python 3.13+
* Django (latest stable LTS or stable version)
* PostgreSQL
* Redis
* Celery
* Pillow
* django-ckeditor
* django-imagekit (or an equivalent image processing solution)
* Gunicorn
* Nginx

Do not replace these technologies unless explicitly instructed.

---

# Frontend Stack

Frontend must use only:

* Django Templates
* HTML5
* CSS3
* Vanilla JavaScript (ES6+)

No SPA architecture.

No frontend framework.

No client-side rendering.

Server-side rendering is mandatory.

---

# Forbidden Frontend Technologies

Never use:

* React
* Vue
* Angular
* Next.js
* Nuxt.js
* jQuery
* Alpine.js
* Tailwind CSS
* Material UI
* Bootstrap JavaScript components

Bootstrap CSS may be used only if explicitly approved.

The preferred solution is a custom design system.

---

# CSS Policy

CSS must be written manually.

Every stylesheet must have a single responsibility.

Never place CSS inside HTML templates.

Never generate inline styles.

Separate files by responsibility.

Example:

base.css

variables.css

layout.css

typography.css

header.css

footer.css

cards.css

forms.css

tables.css

buttons.css

utilities.css

responsive.css

cms.css

---

# JavaScript Policy

JavaScript must also be modular.

Never place JavaScript directly inside templates.

Never generate inline scripts.

Separate files by functionality.

Example:

main.js

menu.js

search.js

modal.js

dropdown.js

tabs.js

toast.js

cropper.js

editor.js

dashboard.js

cms.js

forms.js

validation.js

Every file should perform only one task.

---

# HTML Policy

Templates must remain clean.

Business logic must never exist inside HTML.

Avoid deeply nested template structures.

Prefer reusable includes.

Use semantic HTML.

Example:

<header>

<nav>

<main>

<section>

<article>

<aside>

<footer>

Accessibility should always be considered.

---

# Django Templates

Always extend:

base.html

Never duplicate page layout.

Reusable components must be extracted.

Examples:

header.html

footer.html

sidebar.html

breadcrumb.html

pagination.html

news_card.html

category_card.html

author_card.html

advertisement.html

search_form.html

Every reusable block should become a component.

---

# Database

Database engine:

PostgreSQL

Never use SQLite in production.

All models should be normalized.

Avoid duplicated data.

Indexes must be added where necessary.

Use ForeignKey appropriately.

Avoid storing derived information whenever possible.

---

# Image Processing

Every uploaded image must follow the same pipeline.

Upload

↓

Validation

↓

Crop

↓

Resize

↓

Optimization

↓

Convert to WebP

↓

Generate thumbnails

↓

Store

Original images should never be served directly to users.

---

# CKEditor

Use a simplified CKEditor configuration.

Enable only:

Headings

Bold

Italic

Underline

Lists

Tables

Links

Images

Videos

Blockquote

Alignment

Remove unnecessary buttons.

The editor should remain clean and easy to use.

---

# Cropper

Every uploaded image should open inside Cropper before saving.

Supported actions:

Crop

Zoom

Rotate

Reset

Preview

The crop result should become the final uploaded image.

---

# Media Formats

Allowed image formats:

JPEG

PNG

WEBP

Automatically convert:

JPEG → WEBP

PNG → WEBP

SVG files should not be converted.

---

# File Storage

Separate uploaded files from static assets.

Structure:

media/

uploads/

news/

categories/

pages/

users/

ads/

thumbnails/

webp/

Static files:

static/

css/

js/

icons/

fonts/

images/

Never mix static assets with uploaded media.

---

# API Policy

The project is primarily server-rendered.

Do not create REST API endpoints unless required for AJAX functionality.

AJAX endpoints should remain minimal.

Avoid unnecessary APIs.

---

# Browser Support

Support:

Latest Chrome

Latest Edge

Latest Firefox

Latest Safari

Graceful degradation for older browsers is acceptable.

---

# Development Environment

Development should support:

Linux

Windows

macOS

Configuration values must be stored in environment variables.

Never hardcode secrets.

---

# Package Management

Use:

pip

requirements.txt

Dependencies should remain minimal.

Every dependency must be justified.

Avoid packages that are no longer maintained.

---

# Logging

Use Django logging.

Separate logs by type:

Application

Security

Errors

Background Tasks

Logs should be readable and structured.

---

# Error Handling

Never expose stack traces to users.

Display custom error pages:

404

403

500

Errors should always be logged.

---

# Final Technology Rule

Technology choices must always favor:

Reliability

Maintainability

Performance

Scalability

Security

If multiple implementation options exist, always choose the simplest solution that satisfies these principles.
# CLAUDE.md

# Chapter 4 — Project Architecture

## Architecture Philosophy

The architecture of this project must prioritize long-term maintainability, scalability and code readability.

Every module must have a single responsibility.

Every feature should belong to a clearly defined application.

Avoid monolithic structures.

Avoid placing unrelated functionality inside the same application.

The project should remain understandable even after years of development.

---

# High-Level Architecture

The project consists of three major layers:

1. Public Website

2. Custom CMS

3. Core System

Each layer must remain independent while sharing common services where appropriate.

---

# Project Directory Structure

The project must follow the structure below.

```text
project/
│
├── apps/
│   ├── accounts/
│   ├── advertisements/
│   ├── categories/
│   ├── cms/
│   ├── core/
│   ├── logs/
│   ├── media_manager/
│   ├── news/
│   ├── pages/
│   ├── seo/
│   ├── settings_app/
│   ├── tags/
│   └── users/
│
├── config/
│
├── templates/
│
├── static/
│
├── media/
│
├── locale/
│
├── requirements/
│
├── docs/
│
├── scripts/
│
├── manage.py
│
└── .env
```

No additional applications should be created without architectural justification.

---

# Django Applications

Every application must have a clearly defined responsibility.

accounts/

Authentication.

Authorization.

Login.

Password reset.

Role checking.

---

users/

CMS user profiles.

Permissions.

Activity information.

---

news/

Articles.

Featured news.

Breaking news.

Scheduled publication.

Related news.

Views counter.

---

categories/

Category tree.

Subcategories.

Navigation.

Category ordering.

---

tags/

Tags.

Tag pages.

Relations to articles.

---

pages/

Static pages.

About.

Contacts.

Privacy Policy.

Terms of Use.

---

advertisements/

Advertisement management.

Banner positions.

Scheduling.

Visibility.

---

media_manager/

Image upload.

Cropper integration.

WebP conversion.

Thumbnail generation.

Media library.

---

seo/

Meta tags.

Sitemap.

Robots.

Canonical URLs.

Open Graph.

Structured data.

---

settings_app/

Website configuration.

Logo.

Favicon.

Social links.

Email settings.

General preferences.

---

logs/

System logs.

Audit logs.

CMS activity logs.

---

cms/

Dashboard.

Management interface.

Widgets.

Statistics.

Internal tools.

---

core/

Shared utilities.

Common mixins.

Helper functions.

Reusable services.

Base classes.

This application should never contain business logic.

---

# Templates Structure

Templates must be organized by application.

Example:

```text
templates/

base.html

components/

home/

news/

categories/

pages/

cms/

accounts/

errors/
```

Each application owns its own templates.

Never place all templates in one directory.

---

# Components Directory

Reusable UI elements belong here.

Example:

```text
templates/components/

header.html

footer.html

sidebar.html

breadcrumb.html

pagination.html

search_form.html

news_card.html

featured_news.html

category_card.html

tag.html

modal.html

toast.html

table.html

button.html

form_field.html

empty_state.html

loading.html
```

If a component is reused more than once, it must be extracted.

---

# Static Files Structure

Static assets must be organized.

```text
static/

css/

js/

fonts/

icons/

images/

vendors/
```

Inside CSS:

```text
css/

base/

layout/

components/

pages/

cms/

utilities/
```

Inside JavaScript:

```text
js/

core/

components/

pages/

cms/

utilities/
```

Avoid placing unrelated files together.

---

# Media Structure

Uploaded files must never mix with static assets.

```text
media/

news/

categories/

pages/

users/

ads/

temp/

thumbnails/

webp/
```

Temporary uploads should be cleaned automatically.

---

# URL Architecture

URLs must remain clean and predictable.

Examples:

/

news/

/news/article-slug/

/category/

/category/subcategory/

/search/

/archive/

/tag/

/about/

/contacts/

CMS:

/cms/

/cms/news/

/cms/categories/

/cms/media/

/cms/users/

/cms/settings/

Never expose implementation details in URLs.

---

# Application Independence

Applications should communicate through models, services or clearly defined interfaces.

Avoid circular dependencies.

Avoid importing unrelated applications directly.

Business logic should remain inside its owning application.

---

# Shared Services

Shared functionality belongs in dedicated services.

Examples:

ImageService

SEOService

NotificationService

CacheService

SearchService

SlugService

ViewCounterService

Services must be reusable.

---

# Configuration

Configuration must never be hardcoded.

Use:

.env

Django settings

Environment variables

Never store:

Passwords

API keys

Secret keys

SMTP credentials

Inside source code.

---

# Signals

Use Django signals only when appropriate.

Allowed examples:

Generate thumbnails.

Create audit logs.

Update search index.

Invalidate cache.

Avoid placing business logic inside signals.

---

# Management Commands

Reusable maintenance tasks should become management commands.

Examples:

Generate sitemap.

Clear cache.

Optimize images.

Remove temporary files.

Backup database.

Rebuild search index.

---

# Background Tasks

Heavy operations must run asynchronously.

Examples:

Image optimization.

WebP conversion.

Thumbnail generation.

Email sending.

Scheduled publishing.

Backup creation.

Use Celery.

Never block user requests with long-running operations.

---

# Documentation

Every major module should contain internal documentation.

Complex business logic must include concise comments explaining the reasoning.

Do not comment obvious code.

Document architecture, not syntax.

---

# Architecture Rules

Never duplicate business logic.

Never bypass application boundaries.

Never place business logic inside templates.

Never place business logic inside JavaScript.

Never create "utility" files containing unrelated code.

Keep every module focused.

The architecture should remain clean, modular and scalable throughout the entire lifetime of the project.
# CLAUDE.md

# Chapter 5 — Django Development Rules

## General Principles

Django is the foundation of this project.

Every implementation must follow Django Best Practices.

Never write code that works only for the current task.

Always implement solutions that remain maintainable as the project grows.

Every decision must prioritize:

* Readability
* Maintainability
* Scalability
* Security
* Performance

---

# Django Version

Always use the latest stable Django release that is officially supported.

Do not use deprecated APIs.

Do not implement legacy patterns.

---

# Application Rules

Every Django application must have a single responsibility.

Never mix unrelated functionality.

Correct examples:

news

categories

tags

accounts

pages

seo

cms

advertisements

media_manager

Incorrect examples:

utils

misc

everything

temp

helpers

Applications must have meaningful names.

---

# Models

Every model must follow these principles:

Single responsibility.

Descriptive field names.

Clear relationships.

Proper indexing.

Business logic belongs inside models or dedicated services when appropriate.

Avoid duplicated fields.

Avoid storing calculated values unless performance requires it.

---

# Base Model

All models should inherit from a common abstract base model.

The base model should contain common fields such as:

* created_at
* updated_at
* created_by (where applicable)
* updated_by (where applicable)

Do not duplicate these fields across models.

---

# Model Naming

Model names must always be singular.

Correct:

News

Category

Tag

Advertisement

Page

Incorrect:

NewsModel

Categories

ArticlesTable

Use clear English names for models and fields.

---

# Field Naming

Field names must be descriptive.

Correct:

title

slug

short_description

published_at

featured_image

Incorrect:

t

desc

img

d

Never abbreviate names without a strong reason.

---

# Relationships

Use relationships appropriately.

One-to-Many:

ForeignKey

Many-to-Many:

ManyToManyField

One-to-One:

OneToOneField

Avoid unnecessary relationships.

Avoid duplicate data.

---

# Query Optimization

Always optimize database queries.

Use:

select_related()

prefetch_related()

only()

defer()

annotate()

when appropriate.

Never perform N+1 queries.

Database efficiency is mandatory.

---

# Managers

Complex queries should be moved into custom managers or querysets.

Views should remain simple.

Business filtering logic should never be duplicated across multiple views.

---

# Views

Use Class-Based Views (CBV) by default.

Function-Based Views (FBV) may be used only when they provide a significantly simpler implementation.

Views must remain thin.

Views should coordinate work, not contain business logic.

---

# Business Logic

Business logic must never live inside views.

Instead use:

Models

Services

Managers

Utility classes (only for generic reusable functionality)

Views should call these layers rather than implement complex logic directly.

---

# Forms

Use Django Forms or ModelForms where appropriate.

All forms must include:

Server-side validation.

Helpful validation messages.

Clear field labels.

Consistent styling.

Never trust client-side validation alone.

---

# Validation

Validation must occur:

Client-side (for better UX).

Server-side (mandatory).

Server-side validation always has higher priority.

Never assume client input is safe.

---

# Templates

Templates should contain presentation only.

Never write business logic inside templates.

Avoid deeply nested conditions.

Prefer reusable template components.

Keep templates readable.

---

# Context Data

Pass only the data required by the template.

Avoid sending unnecessary objects.

Avoid excessive context variables.

Use meaningful variable names.

---

# URL Configuration

URLs must be organized by application.

Example:

news/urls.py

categories/urls.py

cms/urls.py

Include them in the main URL configuration.

Avoid placing all routes in a single file.

---

# Slugs

Use slugs for public URLs.

Every slug must be:

Readable.

Unique.

SEO-friendly.

Automatically generated when possible.

Allow manual editing when necessary.

---

# Pagination

Large datasets must always use pagination.

Never load thousands of records on a single page.

Pagination should be reusable across the project.

---

# Search

Search functionality should be isolated.

Search logic must never be duplicated.

Search should support:

Title

Content

Category

Tags

Search implementation should remain efficient as data grows.

---

# Permissions

Permissions must be checked on the server.

Never rely on hiding buttons.

Every protected action must verify permissions before execution.

Unauthorized access must always return the correct HTTP response.

---

# Error Handling

Handle exceptions gracefully.

Never expose stack traces to end users.

Log unexpected exceptions.

Display user-friendly error messages.

---

# Transactions

Use database transactions for operations that modify multiple related records.

Partial updates must never leave the database in an inconsistent state.

---

# Caching

Implement caching strategically.

Suitable examples:

Homepage.

Popular articles.

Category lists.

Navigation.

Site settings.

Do not cache user-specific or permission-sensitive data unless properly designed.

---

# Signals

Signals should remain lightweight.

Appropriate uses include:

Creating audit logs.

Generating thumbnails.

Clearing cache.

Scheduling background tasks.

Avoid implementing business workflows inside signals.

---

# Celery Tasks

Long-running operations must execute asynchronously.

Examples:

Image processing.

WebP conversion.

Scheduled publishing.

Email notifications.

Database backups.

Views must return responses quickly without waiting for background processing.

---

# Logging

Important actions must be logged.

Examples:

Login.

Logout.

Article creation.

Article editing.

Article deletion.

Category changes.

User management.

System settings updates.

Logs should include:

Timestamp.

User.

Action.

Target object.

IP address when appropriate.

---

# Testing Readiness

Code must be written in a way that allows future automated testing.

Avoid tightly coupled implementations.

Functions and services should be easy to test independently.

---

# Django Best Practices

Always follow:

Fat models where appropriate.

Thin views.

Reusable services.

Clear separation of concerns.

Predictable naming.

Consistent structure.

Avoid unnecessary abstraction.

Avoid premature optimization.

---

# Final Django Rule

Every Django implementation must look as if it was written by an experienced Django engineering team.

Code should be clean, modular, scalable and production-ready.

No shortcuts.

No temporary implementations.

No demo-quality code.

Every file should be suitable for long-term commercial maintenance.
# CLAUDE.md

# Chapter 6 — HTML & Django Templates Standards

## General Philosophy

HTML is responsible only for structure and presentation.

Business logic must never exist inside templates.

Templates should remain clean, readable and reusable.

Every template should be understandable within a few minutes by a new developer.

Prefer simplicity over clever template code.

---

# HTML5 Standard

All pages must use valid HTML5.

Use semantic elements whenever possible.

Preferred elements include:

* header
* nav
* main
* section
* article
* aside
* footer
* figure
* figcaption
* time
* address

Avoid excessive use of generic `<div>` elements when semantic alternatives exist.

---

# Base Template

Every public page must inherit from:

```text
base.html
```

Every CMS page must inherit from:

```text
cms/base.html
```

Do not duplicate page layouts.

The base template is responsible for:

* Document structure
* Meta tags
* CSS loading
* JavaScript loading
* Header
* Footer
* Global notifications
* Global modals

---

# Template Inheritance

Always use Django template inheritance.

Correct structure:

```text
base.html

↓

page.html

↓

components
```

Never duplicate common page sections.

---

# Template Includes

Reusable UI blocks must be extracted.

Examples:

```text
components/header.html

components/footer.html

components/sidebar.html

components/breadcrumb.html

components/news_card.html

components/category_card.html

components/pagination.html

components/search_form.html

components/modal.html

components/toast.html
```

If the same HTML appears twice, it should become a reusable component.

---

# Template Organization

Templates must be grouped by application.

Example:

```text
templates/

news/

categories/

pages/

cms/

accounts/

errors/

components/
```

Avoid placing all templates inside a single directory.

---

# Naming Convention

Template names must clearly describe their purpose.

Correct:

```text
home.html

news_detail.html

category_list.html

search_results.html

contact.html
```

Incorrect:

```text
page.html

index2.html

temp.html

newpage.html
```

Names should be descriptive and predictable.

---

# HTML Formatting

Use consistent indentation.

Indent with four spaces.

Each nested level increases indentation by one level.

Opening and closing tags should align vertically.

Avoid unnecessarily deep nesting.

Maximum recommended nesting depth:

Five levels.

If deeper nesting occurs, refactor the structure.

---

# Template Logic

Keep template logic minimal.

Allowed:

* if
* for
* include
* block
* extends
* url
* static

Avoid complex nested conditions.

Do not perform calculations inside templates.

Do not implement business rules inside templates.

---

# Context Variables

Context variables should have meaningful names.

Correct:

```text
article

category

popular_news

featured_news
```

Incorrect:

```text
a

obj

item1

data
```

Template variables should immediately communicate their purpose.

---

# Forms

All forms must use Django Forms or ModelForms.

Every form should include:

* Labels
* Help text where useful
* Validation messages
* CSRF protection

Never disable CSRF protection.

---

# Accessibility

Accessibility is mandatory.

Every image must have an alt attribute.

Every form control must have a label.

Buttons should have descriptive text.

Navigation should be keyboard accessible.

Color must never be the only way to communicate meaning.

---

# Images

Use responsive images.

Lazy loading must be enabled for content images where appropriate.

Example requirements:

* Width and height attributes should be provided when possible.
* Images should not cause layout shifts.
* Images should always use optimized WebP versions if available.

Decorative images should use empty alt attributes.

Informative images should have meaningful descriptions.

---

# Links

Internal links must use Django URL names.

Correct:

```django
{% url 'news:detail' article.slug %}
```

Never hardcode internal URLs.

External links should clearly indicate when they leave the website if required by UX.

---

# Navigation

The navigation menu must be generated dynamically.

Categories and subcategories should come from the database.

The menu should support:

* Active state
* Hover state
* Keyboard navigation
* Responsive behavior

Avoid hardcoded menu structures.

---

# Breadcrumbs

Every page below the homepage must display breadcrumbs.

Examples:

```text
Home

↓

Category

↓

Subcategory

↓

Article
```

Breadcrumbs should be generated dynamically.

---

# Cards

News cards should always have the same structure.

Standard news card:

* Featured image
* Category
* Title
* Short description
* Publication date
* View count

Optional:

* Author
* Breaking badge
* Featured badge

All cards should remain visually consistent.

---

# Tables

CMS tables must use reusable table components.

Requirements:

* Sortable columns
* Pagination
* Responsive behavior
* Hover state
* Empty state
* Loading state

Never duplicate table markup across pages.

---

# Empty States

Every page that may have no data must display a proper empty state.

Example:

No articles found.

No categories available.

No search results.

Provide a helpful explanation or next action.

Never leave pages visually empty.

---

# Error Pages

Create custom templates for:

* 403
* 404
* 500

They must follow the same design language as the rest of the website.

Do not display technical details.

---

# CMS Templates

CMS templates should be separate from public templates.

Structure example:

```text
cms/

base.html

dashboard.html

news/

categories/

users/

settings/

media/
```

Never mix CMS templates with public website templates.

---

# Responsive HTML

HTML structure should support responsive layouts naturally.

Avoid markup that only works on desktop.

Content order should remain logical on smaller screens.

---

# Performance

Avoid unnecessary HTML elements.

Reduce DOM complexity.

Keep the document structure efficient.

Large pages should remain easy to render.

---

# Comments

Use HTML comments only when they improve maintainability.

Do not leave temporary comments.

Do not leave commented-out code.

Example:

```html
<!-- Featured News Section -->
```

Avoid obvious comments.

---

# Final HTML Rule

Every HTML template must be:

* Semantic
* Accessible
* Modular
* Reusable
* Readable
* Responsive
* Lightweight
* Production-ready

Templates should reflect professional engineering standards and integrate seamlessly with the overall Django architecture.
# CLAUDE.md

# Chapter 7 — CSS Architecture & Styling Standards

## General Philosophy

CSS must be written as a scalable design system, not as page-specific styling.

Every style should be reusable.

Every component should have predictable behavior.

The visual language of the website must remain consistent across all public pages and the CMS.

CSS should be easy to navigate, easy to maintain and easy to extend.

Never sacrifice maintainability for shorter code.

---

# CSS Methodology

The project must follow a component-based architecture inspired by BEM principles.

Class names must be descriptive.

Example:

```text
.news-card
.news-card__image
.news-card__title
.news-card__meta
.news-card__description
.news-card--featured
```

Avoid generic class names.

Incorrect:

```text
.box
.item
.red
.style1
.block
.test
```

Every class name should clearly describe its purpose.

---

# File Structure

CSS files must be organized as follows:

```text
static/css/

base/
│
├── reset.css
├── variables.css
├── typography.css
├── animations.css
└── utilities.css

layout/
│
├── container.css
├── grid.css
├── header.css
├── footer.css
├── sidebar.css
└── navigation.css

components/
│
├── buttons.css
├── cards.css
├── forms.css
├── tables.css
├── modal.css
├── dropdown.css
├── pagination.css
├── breadcrumbs.css
├── toast.css
├── badges.css
└── alerts.css

pages/
│
├── home.css
├── article.css
├── category.css
├── search.css
├── contacts.css
└── about.css

cms/
│
├── dashboard.css
├── editor.css
├── media.css
├── users.css
├── settings.css
└── tables.css

responsive/
│
├── desktop.css
├── tablet.css
└── mobile.css
```

Never place all styles inside a single file.

---

# CSS Variables

All reusable values must use CSS variables.

Store in:

```text
variables.css
```

Examples:

* Colors
* Font sizes
* Border radius
* Shadows
* Spacing
* Transition duration
* Z-index values
* Container width

Never duplicate constant values throughout the project.

---

# Colors

Primary Color

Red

Secondary Color

Dark Gray

Background

White

Surface

Light Gray

Text

Dark Gray

Border

Soft Gray

Success

Green

Warning

Orange

Danger

Red

Information

Blue

Never use random colors.

Every color must come from the design system.

---

# Typography

Use one primary font family across the project.

Preferred font:

Inter

Fallback:

system-ui

sans-serif

Typography scale must be consistent.

Example:

H1

H2

H3

H4

Body Large

Body

Small

Caption

Avoid arbitrary font sizes.

---

# Spacing System

Use an 8px spacing system.

Examples:

4px

8px

16px

24px

32px

40px

48px

64px

80px

96px

Never use random spacing values.

---

# Grid System

Desktop container:

1320px

Grid:

12 columns

Gap:

24px

Tablet:

8 columns

Mobile:

4 columns

Layouts must align consistently across pages.

---

# Border Radius

Use consistent radius values.

Example:

Small

6px

Medium

10px

Large

16px

Cards, buttons and inputs should follow the same visual language.

---

# Shadows

Use subtle shadows only.

Never create heavy floating effects.

Shadow levels:

Small

Medium

Large

Every shadow must originate from the design system.

---

# Buttons

Every button must support:

Default

Hover

Focus

Active

Disabled

Loading

Button types:

Primary

Secondary

Outline

Danger

Success

Ghost

Icon Button

Buttons must have consistent height.

---

# Forms

All form controls should share the same styling.

Include:

Text Input

Textarea

Select

Checkbox

Radio

Switch

Date Picker

File Upload

Validation States

Error States

Disabled States

Focus States

Consistency is mandatory.

---

# Tables

CMS tables must include:

Hover state

Selected row

Striped rows (optional)

Sortable headers

Responsive scrolling

Empty state

Loading state

Tables should remain readable with large datasets.

---

# Cards

Every card component must share a common structure.

News cards

Category cards

Statistic cards

Advertisement cards

Author cards

Cards should never have inconsistent spacing.

---

# Animations

Animations must improve usability.

Allowed:

Fade

Slide

Scale

Opacity

Transform

Avoid:

Flash

Bounce

Shake

Excessive rotation

Animations should never distract users.

---

# Transitions

Standard transition duration:

200–300ms

Transitions should be smooth and consistent.

Avoid different timings across components.

---

# Icons

Use Bootstrap Icons only.

Icons should:

Align properly

Use consistent sizing

Match surrounding text

Avoid mixing icon libraries.

---

# Responsive Design

Desktop First approach.

Breakpoints:

Desktop

1440px+

Laptop

1200px

Tablet

992px

Mobile Large

768px

Mobile

576px

Small Mobile

360px

Layouts should adapt naturally.

Never hide critical functionality on smaller screens.

---

# Utility Classes

Utility classes should remain minimal.

Examples:

.text-center

.d-flex

.hidden

.mt-16

.mb-24

.w-100

Avoid creating hundreds of utility classes.

Component styles remain the priority.

---

# CMS Styling

CMS must have its own stylesheet hierarchy.

Do not mix CMS styles with public website styles.

Shared components may inherit from common component styles where appropriate.

---

# Print Styles

Provide dedicated print styles for pages that may be printed.

Examples:

Articles

Reports

System exports

Hide unnecessary interface elements.

---

# Dark Mode

Dark mode is not part of the first release.

Do not implement dark mode architecture unless explicitly requested.

---

# Performance

Minimize CSS duplication.

Avoid overly specific selectors.

Avoid !important except in exceptional cases.

Keep selector depth shallow.

Optimize for rendering performance.

---

# Code Formatting

Indent using four spaces.

One declaration per line.

Group related properties logically.

Example order:

Position

Display

Box Model

Typography

Visual

Animation

Miscellaneous

Maintain consistent formatting across all files.

---

# Final CSS Rule

Every stylesheet must be:

Modular

Reusable

Predictable

Scalable

Consistent

Readable

Production-ready

The CSS architecture should support years of future development without requiring major refactoring.
# CLAUDE.md

# Chapter 8 — JavaScript Architecture & Development Standards

## General Philosophy

JavaScript must enhance the user experience, not control the entire application.

The project is server-side rendered using Django Templates.

JavaScript is responsible for interactivity only.

Never move business logic from Django to JavaScript.

Never use JavaScript to replace proper backend implementation.

The website must remain usable even if JavaScript is temporarily unavailable whenever reasonably possible.

---

# JavaScript Standard

Use only:

* Vanilla JavaScript (ES6+)

Do not use:

* jQuery
* React
* Vue
* Angular
* Alpine.js
* Stimulus
* Knockout
* Backbone

No frontend framework is allowed.

---

# File Structure

JavaScript must be organized into small, focused modules.

```text
static/js/

core/
│
├── app.js
├── config.js
├── utils.js
└── api.js

components/
│
├── dropdown.js
├── modal.js
├── tabs.js
├── accordion.js
├── toast.js
├── tooltip.js
├── pagination.js
├── search.js
├── breadcrumbs.js
└── lazyload.js

pages/
│
├── home.js
├── article.js
├── category.js
├── contacts.js
├── search.js
└── about.js

cms/
│
├── dashboard.js
├── editor.js
├── media.js
├── users.js
├── settings.js
├── categories.js
├── news.js
└── analytics.js
```

Never place all JavaScript inside one file.

---

# Loading Strategy

Load JavaScript only where it is required.

Global scripts belong in:

app.js

Page-specific functionality belongs only to its corresponding page module.

Avoid loading unnecessary scripts.

---

# Inline JavaScript

Never write JavaScript directly inside HTML.

Forbidden:

```html
<button onclick="saveNews()">
```

Correct:

Use event listeners inside JavaScript modules.

Templates must remain clean.

---

# Global Variables

Avoid global variables.

Use modules.

Use block scope.

Prefer:

const

Use:

let

only when reassignment is required.

Never use:

var

---

# DOM Access

Cache frequently used DOM elements.

Avoid repeated DOM queries.

Always verify element existence before attaching events.

Example principle:

Query once.

Reuse many times.

---

# Event Listeners

Use addEventListener().

Never overwrite events.

Remove listeners when necessary.

Avoid duplicated listeners.

---

# Component Initialization

Every component must initialize independently.

Example:

Dropdown

Modal

Tabs

Search

Toast

Accordion

Each component should expose a clear initialization method.

Avoid giant initialization files.

---

# AJAX

Use Fetch API.

Do not use XMLHttpRequest.

AJAX should be used only when necessary.

Examples:

Search suggestions

CMS actions

Image uploads

Live validation

Notifications

Do not replace normal page navigation with AJAX.

---

# Error Handling

Every asynchronous operation must handle:

Success

Failure

Network error

Timeout

Unexpected response

Never fail silently.

Display user-friendly messages.

Log technical details when appropriate.

---

# Form Validation

Client-side validation exists only for user convenience.

Server-side validation is mandatory.

Client validation should:

Prevent obvious mistakes.

Provide immediate feedback.

Never replace backend validation.

---

# Notifications

Use reusable Toast notifications.

Support:

Success

Error

Warning

Information

Toast notifications should:

Appear in the top-right corner.

Disappear automatically.

Support manual dismissal.

Never use browser alert().

---

# Modals

All modals must use the shared modal component.

Support:

Open

Close

ESC key

Overlay click

Focus trapping

Prevent background scrolling.

Never duplicate modal logic.

---

# Search

Search JavaScript should remain lightweight.

Possible responsibilities:

Autocomplete

Live suggestions

Recent searches

Highlighting

Actual search logic belongs to Django.

---

# Navigation

JavaScript may enhance navigation.

Examples:

Mobile menu

Dropdown menus

Sticky header

Smooth scrolling

Navigation must remain functional without unnecessary complexity.

---

# CMS JavaScript

CMS functionality should be modular.

Examples:

Article editor

Media manager

Table filters

Bulk actions

Dashboard widgets

Settings

Every module should be independent.

---

# Image Upload

Upload flow:

Select file

↓

Validate

↓

Cropper

↓

Preview

↓

Upload

↓

Progress indicator

↓

Completion

Provide clear user feedback during every stage.

---

# CKEditor Integration

Keep configuration minimal.

Only enable required plugins.

Do not overload the editor interface.

Editor configuration belongs in a dedicated module.

---

# Data Attributes

Use HTML data attributes for communication.

Example:

data-id

data-slug

data-action

Avoid embedding JavaScript values directly into scripts.

---

# Performance

Minimize DOM manipulation.

Batch updates when possible.

Debounce expensive operations.

Throttle scroll and resize handlers.

Use requestAnimationFrame() where appropriate.

Avoid layout thrashing.

---

# Accessibility

JavaScript must preserve accessibility.

Support:

Keyboard navigation

Focus management

Screen readers

ARIA updates when necessary

Interactive elements must remain accessible.

---

# Browser Storage

Use Local Storage only when appropriate.

Examples:

Theme preference (future)

CMS sidebar state

Draft recovery

Do not store sensitive information.

Avoid excessive browser storage.

---

# Security

Never trust client-side data.

Escape user-generated content.

Protect against XSS.

Include CSRF tokens in AJAX requests.

Never expose secrets in JavaScript.

---

# Code Organization

Each file should solve one problem.

Functions should be short.

Function names should clearly describe behavior.

Avoid deeply nested code.

Separate business logic from UI behavior.

---

# Naming Convention

Use camelCase.

Examples:

openModal()

saveArticle()

toggleSidebar()

initializeEditor()

Avoid unclear names.

Examples to avoid:

run()

go()

test()

temp()

---

# Comments

Comment only complex logic.

Avoid obvious comments.

Write comments explaining why, not what.

---

# Logging

Use console logging only during development.

Production code must not contain unnecessary console.log() statements.

---

# Progressive Enhancement

Every feature should enhance the website rather than replace core functionality.

The primary experience should always come from Django-rendered HTML.

JavaScript should improve usability without becoming a dependency for basic navigation.

---

# Final JavaScript Rule

Every JavaScript module must be:

Small

Modular

Reusable

Readable

Maintainable

Accessible

Secure

Performance-oriented

Production-ready

JavaScript should never dominate the architecture.

Django remains the primary application framework, while JavaScript provides focused enhancements that improve the overall user experience.
# CLAUDE.md

# Chapter 9 — CMS Architecture & Editorial Workflow

## CMS Philosophy

The CMS is the heart of the News Portal.

It is not a customized Django Admin.

It is a completely custom editorial management system built specifically for journalists, editors and administrators.

The CMS must prioritize:

* Speed
* Simplicity
* Productivity
* Reliability
* Consistency

Editors should be able to perform daily work with minimal clicks.

The interface should remain clean even when managing tens of thousands of records.

---

# General Layout

Every CMS page must inherit from:

```text
templates/cms/base.html
```

The layout consists of:

* Left Sidebar
* Top Navigation Bar
* Main Content Area
* Right Utility Panel (optional)
* Global Toast Notifications
* Global Modal System

The layout must remain consistent across every CMS page.

---

# Sidebar

The sidebar is permanently visible on desktop.

On tablets and mobile devices it becomes collapsible.

Sidebar menu order:

```text
Dashboard

News

Categories

Tags

Media Library

Advertisements

Pages

SEO

Users

Activity Logs

Settings

Profile

Logout
```

Only authorized users may see restricted sections.

---

# Top Navigation

The top navigation contains:

* Global search
* Quick create button
* Notifications
* User profile
* Theme placeholder (future)
* Current user information

The top navigation must remain lightweight.

---

# Dashboard

The dashboard is the first page after login.

Widgets include:

Latest Articles

Scheduled Articles

Draft Articles

Published Today

Most Viewed Articles

Recent Activity

Storage Usage

System Status

Recent Logins

Quick Actions

Dashboard widgets should be modular.

Widgets can be reordered in future versions.

---

# User Roles

Supported roles:

Administrator

Editor-in-Chief

Editor

Journalist

Content Manager

Each role has clearly defined permissions.

Permissions must always be enforced on the backend.

The frontend should never be responsible for access control.

---

# Authentication

The CMS must include:

Secure Login

Logout

Password Reset

Password Change

Session Timeout

Remember Me

Optional Two-Factor Authentication (future)

Authentication should use Django authentication mechanisms.

---

# News Management

News management is the primary CMS feature.

Supported operations:

Create

Edit

Preview

Save Draft

Schedule

Publish

Unpublish

Archive

Duplicate

Delete

Restore

Bulk Actions

Every action must be logged.

---

# News Editor

The article editor consists of:

Main Content

Publication Panel

SEO Panel

Featured Image

Gallery

Categories

Tags

Author

Publication Date

Status

Slug

Excerpt

The editor should never feel crowded.

Frequently used actions should remain visible.

---

# CKEditor

The editor uses CKEditor.

Toolbar should remain minimal.

Enable:

Headings

Bold

Italic

Underline

Lists

Links

Tables

Images

Videos

Quotes

Alignment

Remove unnecessary plugins.

Editors should not be overwhelmed.

---

# Categories

Support hierarchical categories.

Structure:

Category

↓

Subcategory

Only two levels are supported.

Category ordering is managed manually.

Navigation updates automatically.

---

# Tags

Tags are independent entities.

Editors can:

Create

Edit

Merge

Delete

Assign

Tag suggestions should be available while editing articles.

---

# Media Library

The media library supports:

Upload

Preview

Search

Filter

Crop

Replace

Delete

WebP conversion

Thumbnail generation

Folder organization

Media items should display:

Preview

Filename

Dimensions

File size

Upload date

Usage count

---

# Advertisements

Advertisement management includes:

Banner positions

Display scheduling

Activation

Expiration

Visibility

Click tracking (future)

Advertisements should never require template modifications.

---

# SEO Management

Each article supports:

Meta Title

Meta Description

Meta Keywords (optional)

Canonical URL

Open Graph Title

Open Graph Description

Open Graph Image

Robots directives

SEO preview should be displayed before publishing.

---

# User Management

Administrators can:

Create users

Edit users

Deactivate users

Reset passwords

Assign roles

View activity

Permission changes should be logged automatically.

---

# Activity Logs

The CMS must log important events.

Examples:

Login

Logout

Article Created

Article Updated

Article Deleted

Category Changed

Settings Updated

User Created

Role Changed

Logs include:

Timestamp

User

Action

Object

IP Address

Status

Logs are read-only.

---

# Settings

General settings include:

Website Name

Logo

Favicon

Footer Information

Social Links

Contact Information

SMTP Settings

Analytics Code

Advertisement Settings

Maintenance Mode

Settings should be grouped logically.

---

# Search

CMS search supports:

Articles

Categories

Tags

Users

Media

Pages

Search results should appear quickly.

---

# Tables

All management pages use a common table component.

Features:

Pagination

Sorting

Filtering

Bulk Selection

Bulk Actions

Search

Responsive Layout

Empty State

Loading State

No page should implement custom table behavior independently.

---

# Bulk Actions

Supported examples:

Delete

Publish

Archive

Move Category

Assign Tags

Restore

Confirmation dialogs are mandatory.

Bulk operations should be optimized.

---

# Notifications

All actions display toast notifications.

Supported types:

Success

Error

Warning

Information

Never use browser alerts.

---

# Confirmation Dialogs

Destructive actions require confirmation.

Examples:

Delete

Archive

Deactivate User

Clear Cache

Reset Settings

Dialogs should clearly explain consequences.

---

# Responsive CMS

Desktop is the primary target.

Tablet support is mandatory.

Mobile support should remain functional for quick editorial tasks.

Complex editing is optimized for desktop.

---

# Performance

Large datasets should remain responsive.

Use:

Pagination

Lazy Loading

Server-side Filtering

Optimized Queries

Background Tasks

Avoid rendering unnecessary data.

---

# Security

Every CMS request requires authentication.

Every action checks permissions.

Sensitive operations require CSRF protection.

Never expose administrative endpoints publicly.

---

# Future Expansion

The CMS architecture must support future modules without redesign.

Examples:

Polls

Newsletters

Comments

Push Notifications

AI Assistance

Analytics

Version History

Workflow Approvals

The architecture should remain extensible.

---

# Final CMS Rule

The CMS must feel like professional editorial software rather than a generic administration panel.

Every screen should improve editorial productivity.

Every workflow should minimize unnecessary actions.

Every interface should remain clean, predictable and consistent.

The CMS is a core product of this project and must be implemented with the same quality standards as the public website.
# CLAUDE.md

# Chapter 10 — Database Architecture & Data Standards

## Database Philosophy

The database is the foundation of the entire system.

Every table, relationship and field must be designed for long-term scalability.

The database must remain normalized, predictable and efficient.

Never design the database only for current requirements.

Always consider future expansion.

Data integrity has higher priority than convenience.

---

# Database Engine

Production database:

PostgreSQL

Development database:

PostgreSQL is strongly preferred.

SQLite may only be used for quick local development if explicitly approved.

Production must never use SQLite.

---

# Database Design Principles

Every model must have:

A single responsibility.

A clear purpose.

Proper relationships.

Descriptive field names.

Meaningful indexes.

Avoid duplicated information.

Avoid unnecessary NULL values.

Use appropriate defaults.

---

# Naming Conventions

Model names:

Singular.

English.

PascalCase.

Examples:

News

Category

Tag

Advertisement

Page

MediaFile

UserProfile

Field names:

snake_case.

Examples:

created_at

updated_at

published_at

featured_image

short_description

Never abbreviate field names.

---

# Primary Keys

Use Django's default auto-generated primary keys unless there is a justified architectural reason to use UUID.

Future migration to UUID should remain possible.

Never expose database IDs unnecessarily in public interfaces.

---

# Foreign Keys

Use ForeignKey whenever a one-to-many relationship exists.

Examples:

Article → Category

Article → Author

Media → User

Advertisement → Position

Always define proper deletion behavior.

Avoid CASCADE unless appropriate.

---

# Many-to-Many Relationships

Use ManyToManyField only where relationships are naturally many-to-many.

Examples:

News ↔ Tags

News ↔ Related Articles

Avoid creating unnecessary junction tables manually.

---

# One-to-One Relationships

Use OneToOneField when extending user-related information.

Example:

User

↓

UserProfile

Authentication data should remain separated from profile information.

---

# Common Model Fields

Most models should include:

created_at

updated_at

created_by

updated_by

is_active

Additional fields should be added only when appropriate.

---

# Soft Delete

Public content should generally use soft deletion.

Examples:

Articles

Pages

Advertisements

Categories

Instead of permanent deletion:

is_deleted = True

Deleted records should remain recoverable.

Permanent deletion should be restricted.

---

# Category Hierarchy

Categories support exactly two levels.

Example:

Politics

↓

International Politics

Technology

↓

Artificial Intelligence

Additional nesting levels are not supported.

The navigation architecture depends on this limitation.

---

# Slugs

Public entities should include slugs.

Examples:

Articles

Categories

Pages

Tags

Slugs must be:

Unique.

Readable.

SEO-friendly.

Automatically generated.

Editable by administrators.

---

# Media Storage

Store only metadata inside the database.

Examples:

Filename

Width

Height

File Size

Format

Alt Text

Caption

Uploaded By

Upload Date

File paths should remain predictable.

---

# Audit Information

Every important modification should be traceable.

Examples:

Created By

Updated By

Published By

Archived By

Deleted By

The database should support future audit requirements.

---

# Status Fields

Avoid boolean fields for workflows.

Instead use status values.

Example:

Draft

Pending Review

Scheduled

Published

Archived

Rejected

Workflow states should remain extensible.

---

# Indexing

Indexes should be added for frequently queried fields.

Examples:

slug

published_at

status

category

created_at

updated_at

Avoid excessive indexing.

Every index should have a measurable purpose.

---

# Constraints

Use database constraints where appropriate.

Examples:

Unique Slugs

Unique Email

Unique Username

Unique Category Order

Data integrity should never rely solely on application logic.

---

# Transactions

Operations affecting multiple records must use database transactions.

Examples:

Publishing articles

Moving categories

Bulk updates

Media replacement

Partial updates must never leave inconsistent data.

---

# Query Optimization

Database queries should be optimized.

Use:

select_related()

prefetch_related()

annotations

database indexes

Never perform unnecessary queries.

Never perform repeated queries inside loops.

---

# Data Integrity

Prevent orphaned records.

Prevent duplicate relationships.

Prevent invalid references.

Validate all foreign keys.

Database consistency is mandatory.

---

# Backup Strategy

The system should support automated backups.

Recommended schedule:

Daily incremental backups.

Weekly full backups.

Monthly archive backups.

Backup verification should be possible.

---

# Migration Policy

Every schema change requires Django migrations.

Never modify production databases manually.

Migration files must be version controlled.

Never delete historical migrations without approval.

---

# Seed Data

Essential data should be generated using management commands.

Examples:

Default administrator.

Default settings.

Default advertisement positions.

Default page templates.

Development data should remain separate.

---

# Search Readiness

Database design should support future search improvements.

Fields should remain searchable.

Relationships should remain index-friendly.

Future integration with Elasticsearch or PostgreSQL Full Text Search should be possible without major redesign.

---

# Scalability

The database should support:

Millions of articles.

Millions of images.

Hundreds of editors.

Millions of visitors.

Architecture should not require redesign as data grows.

---

# Security

Sensitive information must never be stored in plain text.

Passwords use Django authentication.

Secrets belong in environment variables.

Logs should never expose confidential data.

---

# Performance

Optimize for:

Fast reads.

Efficient writes.

Minimal locking.

Efficient indexing.

Low query count.

Database performance should remain stable under heavy traffic.

---

# Future Expansion

The schema should support future modules.

Examples:

Comments

Bookmarks

Reactions

Newsletters

Polls

Notifications

Version History

AI-generated summaries

No future feature should require redesigning the core database.

---

# Final Database Rule

The database must be designed as if it will support a commercial news platform for many years.

Every table should have a clear purpose.

Every relationship should be meaningful.

Every field should exist for a reason.

The database architecture must remain reliable, scalable, secure and easy to maintain throughout the lifetime of the project.
# CLAUDE.md

# Chapter 11 — UI Components & Design System Standards

## General Philosophy

The entire user interface must be built as a component-based design system.

Every visual element should be reusable.

Every component should behave consistently throughout the project.

Never duplicate UI implementations.

If a component appears more than once, it must become a reusable component.

The Design System is the single source of truth for the entire application.

---

# Component Principles

Every component must be:

Reusable.

Predictable.

Accessible.

Responsive.

Independent.

Easy to maintain.

Easy to extend.

Production-ready.

Components should never depend on page-specific implementations.

---

# Component Structure

Each component should have:

HTML template

CSS

JavaScript (only if required)

Documentation

Components must never contain business logic.

---

# Component Categories

The Design System consists of:

Layout Components

Navigation Components

Content Components

Form Components

Feedback Components

Data Components

Media Components

CMS Components

---

# Layout Components

Mandatory layout components:

Header

Footer

Container

Section

Grid

Sidebar

Topbar

Page Header

Content Wrapper

Page Title

Spacing Utilities

These components define the overall page structure.

---

# Navigation Components

Reusable navigation elements:

Primary Navigation

Secondary Navigation

Mobile Navigation

Breadcrumbs

Pagination

Tabs

Dropdown Menu

Context Menu

Category Navigation

Subcategory Navigation

Navigation must remain consistent across the entire project.

---

# Content Components

Content presentation components:

News Card

Featured News Card

Breaking News Card

Category Card

Author Card

Advertisement Card

Tag Badge

Related Articles

Article Meta

Article Gallery

Share Buttons

Content components should never have multiple visual styles without justification.

---

# News Card

Standard News Card contains:

Featured Image

Category

Title

Short Description

Publication Date

View Count

Optional:

Breaking Badge

Featured Badge

Author

Estimated Reading Time

Every News Card should use identical spacing and typography.

---

# Form Components

Reusable form components:

Text Input

Textarea

Select

Checkbox

Radio Button

Switch

File Upload

Image Upload

Date Picker

Time Picker

Search Field

Password Field

Every form element should support:

Default

Focus

Error

Success

Disabled

Readonly

Loading

---

# Buttons

Button types:

Primary

Secondary

Outline

Ghost

Danger

Success

Warning

Icon Button

Link Button

Button sizes:

Small

Medium

Large

Every button must support:

Hover

Focus

Active

Disabled

Loading

Never create custom button styles outside the Design System.

---

# Feedback Components

Feedback elements:

Toast

Alert

Modal

Confirmation Dialog

Loading Spinner

Progress Bar

Skeleton Loader

Empty State

Success State

Error State

Feedback components must always communicate clearly.

---

# Data Components

Reusable data presentation:

Table

Statistic Card

Chart Container

Timeline

Activity Feed

Information Panel

List Group

Badge

Chip

Tag

Data presentation should remain visually consistent.

---

# Table Component

The CMS table supports:

Sorting

Filtering

Pagination

Bulk Selection

Bulk Actions

Responsive Layout

Sticky Header

Loading State

Empty State

Table behavior should be identical throughout the CMS.

---

# Modal Component

Every modal supports:

Open

Close

Overlay Click

Escape Key

Focus Trap

Scrollable Content

Footer Actions

Reusable Sizes:

Small

Medium

Large

Extra Large

No custom modal implementations are allowed.

---

# Toast Notifications

Toast notifications support:

Success

Information

Warning

Error

Toast placement:

Top Right

Auto Close

Manual Close

Queue Support

Animation

Never use browser alert().

---

# Empty States

Every empty state contains:

Illustration (optional)

Title

Description

Primary Action

Secondary Action (optional)

Examples:

No Articles

No Categories

No Search Results

No Users

No Media

Never display blank pages.

---

# Loading States

Use Skeleton Loaders whenever appropriate.

Avoid loading spinners for large content blocks.

Loading indicators should closely resemble the final layout.

---

# Media Components

Media Library components:

Image Card

Folder Card

Upload Area

Cropper

Preview Window

File Information Panel

Media Search

Media Filters

All media interactions should remain consistent.

---

# CMS Components

CMS-specific reusable components:

Dashboard Widget

Statistic Card

Sidebar Menu

Top Navigation

Quick Actions

Filter Panel

Bulk Actions Bar

Permission Badge

Role Badge

Status Badge

System Alert

These components must not be duplicated.

---

# Status Badges

Supported statuses:

Draft

Published

Scheduled

Archived

Deleted

Pending Review

Rejected

Status colors must follow the Design System.

---

# Color Usage

Colors must always represent meaning.

Examples:

Green

Success

Red

Danger

Orange

Warning

Blue

Information

Gray

Inactive

Never assign colors randomly.

---

# Icons

Use Bootstrap Icons exclusively.

Icons should:

Align correctly

Have consistent sizing

Maintain consistent stroke weight

Never mix icon libraries.

---

# Responsive Components

Every component must function correctly on:

Desktop

Laptop

Tablet

Mobile

Responsive behavior should be part of the component itself.

---

# Accessibility

Every component must support:

Keyboard Navigation

Screen Readers

Focus Visibility

ARIA Attributes where appropriate

Accessible Color Contrast

Accessibility is mandatory.

---

# Documentation

Each reusable component should include documentation describing:

Purpose

Usage

Supported Variants

Supported Sizes

Parameters

Examples

This documentation should allow future developers to reuse components correctly.

---

# Versioning

The Design System should evolve without breaking existing components.

Avoid changing component APIs unnecessarily.

Prefer extending existing components over creating duplicates.

---

# Future Expansion

The Design System should support future additions.

Examples:

Dark Mode

Charts

AI Widgets

Notifications Panel

Comment Components

Bookmark Components

Poll Components

Future additions should integrate naturally into the existing system.

---

# Final Design System Rule

Every UI element must belong to the Design System.

No standalone components.

No duplicated implementations.

No inconsistent styling.

The entire interface should appear as a single, unified product designed and implemented by one professional design and engineering team.

The Design System is mandatory for both the public website and the CMS.
# CLAUDE.md

# Chapter 12 — Security Standards

## Security Philosophy

Security is a core requirement of this project.

It is not an optional feature.

Every feature must be designed with security in mind from the beginning.

Never add security after implementation.

Prevent vulnerabilities before they can occur.

Assume every user input is potentially malicious.

Never trust client-side validation.

The backend is the only trusted authority.

---

# Authentication

Authentication must use Django's built-in authentication system.

Never implement a custom authentication mechanism without explicit approval.

Passwords must never be stored in plain text.

Always use Django's password hashing system.

Support:

* Secure Login
* Logout
* Password Reset
* Password Change
* Session Expiration

Authentication should remain simple, secure and reliable.

---

# Authorization

Every protected action must verify permissions on the server.

Never rely on hidden buttons or frontend logic.

If a user lacks permission:

Return the correct HTTP response.

Log the attempt when appropriate.

Do not reveal unnecessary information.

Authorization must be checked for:

* Views
* AJAX requests
* File downloads
* Media management
* Bulk actions
* CMS operations
* Settings changes

---

# User Roles

Permissions are role-based.

Examples:

Administrator

Editor-in-Chief

Editor

Journalist

Content Manager

Each role has only the permissions required to perform its work.

Follow the Principle of Least Privilege.

---

# Password Policy

Passwords should satisfy minimum complexity requirements.

Support:

Minimum length.

Strong hashing.

Secure reset.

Secure storage.

Password history and expiration are optional future enhancements.

Never display passwords.

Never email passwords.

---

# CSRF Protection

CSRF protection is mandatory.

Every form must include:

CSRF Token

Every AJAX request must include the CSRF token.

Never disable CSRF protection.

---

# XSS Protection

Escape user-generated content by default.

Never render untrusted HTML unless explicitly sanitized.

CKEditor content must be filtered before rendering.

Avoid:

unsafe HTML

inline JavaScript

unescaped template output

Prevent reflected, stored and DOM-based XSS whenever applicable.

---

# SQL Injection

Always use Django ORM.

Never build SQL queries using string concatenation.

Raw SQL should only be used when absolutely necessary.

Parameterized queries are mandatory.

---

# File Upload Security

Every uploaded file must be validated.

Validate:

Extension.

MIME Type.

File Size.

Image Integrity.

Reject unsupported formats.

Never trust the file extension alone.

---

# Image Processing

Every uploaded image must pass through the processing pipeline:

Validation

↓

Crop

↓

Optimization

↓

WebP Conversion

↓

Thumbnail Generation

↓

Storage

Never serve unvalidated uploads.

---

# Sensitive Files

Never expose:

Environment files

Configuration files

Logs

Backups

Temporary files

Private media

These files must remain inaccessible from the public website.

---

# Environment Variables

Store sensitive information only in environment variables.

Examples:

SECRET_KEY

Database credentials

SMTP credentials

API keys

Redis configuration

Never hardcode secrets.

Never commit secrets to version control.

---

# HTTPS

Production must always use HTTPS.

Redirect HTTP to HTTPS.

Secure cookies should be enabled.

HSTS may be enabled when deployment requirements are satisfied.

---

# Session Security

Use secure session settings.

Recommended:

HttpOnly Cookies

Secure Cookies

Reasonable Session Timeout

Session Rotation after Login

Invalidate sessions after password changes when appropriate.

---

# Input Validation

Validate every input on the server.

Validation includes:

Type

Length

Required fields

Allowed values

Relationships

Business rules

Never trust browser validation.

---

# Output Encoding

Encode dynamic output correctly.

HTML output

Attribute output

JavaScript output

URL output

Prevent output injection.

---

# Logging Security Events

Log important security events.

Examples:

Successful login

Failed login

Password reset

Permission denied

Role changes

Account lock

Settings modifications

Logs should include:

Timestamp

User

Action

IP Address

Status

---

# Rate Limiting

Sensitive endpoints should support rate limiting.

Examples:

Login

Password reset

Search API

AJAX endpoints

Rate limiting helps reduce abuse.

---

# Brute Force Protection

Protect authentication endpoints.

Possible mechanisms:

Temporary lockout

Increasing delay

IP monitoring

Future CAPTCHA support

Protection should remain user-friendly.

---

# Error Messages

Error messages should never reveal sensitive information.

Avoid:

Database details

Stack traces

Internal file paths

Framework versions

Use generic user-facing messages.

Log technical details internally.

---

# Media Access

Public media and private media must remain separated.

Private files should never be directly accessible without authorization.

Future support for protected downloads should remain possible.

---

# CMS Protection

Every CMS route requires authentication.

Permission checks are mandatory.

Sensitive actions require confirmation.

Administrative pages must never be cached publicly.

---

# Dependencies

Only actively maintained dependencies should be installed.

Remove unused packages.

Keep dependencies updated.

Monitor security advisories.

Avoid abandoned libraries.

---

# Backup Security

Backups must be protected.

Encrypt backups when appropriate.

Restrict backup access.

Regularly verify backup integrity.

Never expose backups publicly.

---

# Audit Trail

Critical actions should be auditable.

Examples:

User creation

Role changes

Settings updates

Article deletion

Permission modifications

Audit logs should be tamper-resistant.

---

# Server Security

Production recommendations:

Run behind Nginx.

Use Gunicorn.

Restrict unnecessary ports.

Use a firewall.

Disable debug mode.

Protect administrative services.

Keep the operating system updated.

---

# Security Headers

Enable appropriate HTTP security headers.

Examples:

Content Security Policy (where practical)

X-Content-Type-Options

Referrer Policy

X-Frame-Options

Permissions Policy

Security headers should be configured at deployment.

---

# Future Security Features

Architecture should support future enhancements.

Examples:

Two-Factor Authentication

Single Sign-On

Hardware Security Keys

Login Notifications

Device Management

Security Dashboard

No redesign should be required to add these features.

---

# Final Security Rule

Security is mandatory at every layer of the application.

Every feature must be secure by default.

Every request must be validated.

Every permission must be verified.

Every input must be sanitized.

Every output must be encoded.

The project must be developed with a security-first mindset from the first line of code until deployment.
# CLAUDE.md

# Chapter 13 — Performance & Optimization Standards

## Performance Philosophy

Performance is a core feature of this project.

Fast websites provide a better user experience, better SEO rankings and lower server costs.

Every feature must be designed with performance in mind.

Optimization should be considered during development, not after the project is finished.

The goal is to build a news portal that remains fast even with millions of page views.

---

# Performance Goals

Target values:

Desktop Lighthouse Score:

95+

Mobile Lighthouse Score:

90+

Largest Contentful Paint (LCP):

Less than 2.5 seconds.

First Contentful Paint (FCP):

Less than 1.8 seconds.

Interaction to Next Paint (INP):

Less than 200 ms.

Cumulative Layout Shift (CLS):

Less than 0.1.

Time To First Byte (TTFB):

As low as possible.

---

# Backend Performance

Backend responses should remain efficient.

Avoid unnecessary database queries.

Optimize ORM usage.

Keep request processing lightweight.

Expensive operations must execute asynchronously.

Never block HTTP requests with long-running tasks.

---

# Database Optimization

Always optimize database access.

Use:

select_related()

prefetch_related()

annotate()

aggregate()

only()

defer()

Avoid:

N+1 queries.

Repeated queries.

Duplicate filtering.

Loading unnecessary fields.

---

# Query Count

Minimize the number of SQL queries per request.

Target:

Homepage

Minimal query count.

Article page

Minimal query count.

CMS tables

Optimized server-side queries.

Never perform queries inside template loops.

---

# Caching Strategy

Use Redis for caching.

Suitable cache targets:

Homepage

Navigation

Category Tree

Popular Articles

Site Settings

SEO Settings

Advertisement Positions

Avoid caching personalized content unless explicitly designed.

---

# Cache Invalidation

Cache should be invalidated automatically when content changes.

Examples:

Article published

Category updated

Settings changed

Advertisement modified

Never require manual cache clearing for normal editorial work.

---

# Celery Tasks

Background processing should use Celery.

Examples:

Image optimization

WebP conversion

Thumbnail generation

Scheduled publishing

Email sending

Backup creation

Search indexing

Do not execute heavy work during user requests.

---

# Image Optimization

Every uploaded image must:

Be validated.

Be resized.

Be compressed.

Be converted to WebP.

Generate multiple thumbnail sizes.

Images must never be served larger than necessary.

---

# Responsive Images

Generate multiple image sizes.

Serve the appropriate size depending on the device.

Avoid delivering desktop-sized images to mobile users.

---

# Lazy Loading

Enable lazy loading for:

Article images

Gallery images

Advertisement images

Media library thumbnails

Avoid lazy loading critical above-the-fold content.

---

# Static Assets

CSS and JavaScript should be:

Minified in production.

Versioned.

Cached by browsers.

Organized efficiently.

Avoid duplicate assets.

---

# CSS Performance

Load only required styles.

Avoid extremely large stylesheets.

Remove unused CSS.

Avoid excessive selector depth.

Keep rendering efficient.

---

# JavaScript Performance

Load JavaScript with appropriate attributes.

Examples:

defer

module

Avoid render-blocking scripts.

Keep JavaScript bundles small.

Only load page-specific scripts where needed.

---

# Font Optimization

Use only required font weights.

Prefer self-hosted fonts.

Enable:

font-display: swap

Avoid loading unnecessary font families.

---

# HTML Optimization

Generate clean HTML.

Avoid excessive DOM depth.

Reduce unnecessary wrapper elements.

Improve browser rendering efficiency.

---

# Advertisement Performance

Advertisements should:

Load asynchronously where possible.

Not block page rendering.

Reserve layout space to prevent layout shifts.

Avoid degrading user experience.

---

# CMS Performance

Large CMS tables should use:

Pagination

Server-side filtering

Indexed search

Bulk operations

Lazy loading

Never render thousands of rows on one page.

---

# Search Performance

Search should remain fast even with large datasets.

Support efficient indexing.

Prepare architecture for future PostgreSQL Full Text Search or Elasticsearch integration.

Avoid scanning unnecessary records.

---

# Media Library Performance

Support:

Thumbnail generation

Progressive loading

Server-side filtering

Pagination

Folder navigation

Do not load the full media library into memory.

---

# API Performance

AJAX endpoints should:

Return only required data.

Avoid large payloads.

Support pagination where appropriate.

Compress responses when supported by the server.

---

# Compression

Enable server compression.

Recommended:

Gzip

Brotli (preferred when available)

Compress:

HTML

CSS

JavaScript

SVG

JSON

Do not compress already compressed formats unnecessarily.

---

# HTTP Caching

Configure browser caching appropriately.

Examples:

Images

CSS

JavaScript

Fonts

Use cache versioning for updates.

---

# Content Delivery

The architecture should allow future CDN integration.

Examples:

Cloudflare

Amazon CloudFront

Bunny CDN

The application should not require structural changes for CDN adoption.

---

# Memory Usage

Avoid unnecessary memory allocation.

Release temporary objects when appropriate.

Keep long-running background tasks memory-efficient.

---

# Scalability

The application should scale horizontally.

Avoid storing application state in memory.

Use Redis for shared caching and task queues.

Keep services stateless whenever practical.

---

# Monitoring

The architecture should support future monitoring.

Examples:

Application metrics

Slow query detection

Task monitoring

Error tracking

Performance dashboards

Monitoring should require minimal integration effort.

---

# SEO Performance

Performance contributes directly to SEO.

Optimize:

Core Web Vitals

Page speed

Image delivery

Structured HTML

Server response times

Maintain excellent search engine performance.

---

# Production Optimization

Before deployment:

Disable DEBUG.

Collect static files.

Minify assets.

Verify caching.

Optimize database indexes.

Test Lighthouse scores.

Confirm background workers are operational.

---

# Performance Testing

Test under realistic load.

Verify:

Homepage

Article pages

CMS

Media uploads

Search

Scheduled publishing

Performance should remain stable as traffic increases.

---

# Future Optimization

Architecture should support future enhancements.

Examples:

Edge caching

Image CDN

Object storage

Read replicas

Search clusters

Queue scaling

No major architectural redesign should be required.

---

# Final Performance Rule

Every implementation must consider performance before writing code.

Fast code is preferred.

Efficient queries are mandatory.

Background processing should handle expensive operations.

The project should remain responsive under high traffic and large datasets.

Performance is not an optimization phase.

Performance is a permanent development requirement.
# CLAUDE.md

# Chapter 13 — Performance & Optimization Standards

## Performance Philosophy

Performance is a core feature of this project.

Fast websites provide a better user experience, better SEO rankings and lower server costs.

Every feature must be designed with performance in mind.

Optimization should be considered during development, not after the project is finished.

The goal is to build a news portal that remains fast even with millions of page views.

---

# Performance Goals

Target values:

Desktop Lighthouse Score:

95+

Mobile Lighthouse Score:

90+

Largest Contentful Paint (LCP):

Less than 2.5 seconds.

First Contentful Paint (FCP):

Less than 1.8 seconds.

Interaction to Next Paint (INP):

Less than 200 ms.

Cumulative Layout Shift (CLS):

Less than 0.1.

Time To First Byte (TTFB):

As low as possible.

---

# Backend Performance

Backend responses should remain efficient.

Avoid unnecessary database queries.

Optimize ORM usage.

Keep request processing lightweight.

Expensive operations must execute asynchronously.

Never block HTTP requests with long-running tasks.

---

# Database Optimization

Always optimize database access.

Use:

select_related()

prefetch_related()

annotate()

aggregate()

only()

defer()

Avoid:

N+1 queries.

Repeated queries.

Duplicate filtering.

Loading unnecessary fields.

---

# Query Count

Minimize the number of SQL queries per request.

Target:

Homepage

Minimal query count.

Article page

Minimal query count.

CMS tables

Optimized server-side queries.

Never perform queries inside template loops.

---

# Caching Strategy

Use Redis for caching.

Suitable cache targets:

Homepage

Navigation

Category Tree

Popular Articles

Site Settings

SEO Settings

Advertisement Positions

Avoid caching personalized content unless explicitly designed.

---

# Cache Invalidation

Cache should be invalidated automatically when content changes.

Examples:

Article published

Category updated

Settings changed

Advertisement modified

Never require manual cache clearing for normal editorial work.

---

# Celery Tasks

Background processing should use Celery.

Examples:

Image optimization

WebP conversion

Thumbnail generation

Scheduled publishing

Email sending

Backup creation

Search indexing

Do not execute heavy work during user requests.

---

# Image Optimization

Every uploaded image must:

Be validated.

Be resized.

Be compressed.

Be converted to WebP.

Generate multiple thumbnail sizes.

Images must never be served larger than necessary.

---

# Responsive Images

Generate multiple image sizes.

Serve the appropriate size depending on the device.

Avoid delivering desktop-sized images to mobile users.

---

# Lazy Loading

Enable lazy loading for:

Article images

Gallery images

Advertisement images

Media library thumbnails

Avoid lazy loading critical above-the-fold content.

---

# Static Assets

CSS and JavaScript should be:

Minified in production.

Versioned.

Cached by browsers.

Organized efficiently.

Avoid duplicate assets.

---

# CSS Performance

Load only required styles.

Avoid extremely large stylesheets.

Remove unused CSS.

Avoid excessive selector depth.

Keep rendering efficient.

---

# JavaScript Performance

Load JavaScript with appropriate attributes.

Examples:

defer

module

Avoid render-blocking scripts.

Keep JavaScript bundles small.

Only load page-specific scripts where needed.

---

# Font Optimization

Use only required font weights.

Prefer self-hosted fonts.

Enable:

font-display: swap

Avoid loading unnecessary font families.

---

# HTML Optimization

Generate clean HTML.

Avoid excessive DOM depth.

Reduce unnecessary wrapper elements.

Improve browser rendering efficiency.

---

# Advertisement Performance

Advertisements should:

Load asynchronously where possible.

Not block page rendering.

Reserve layout space to prevent layout shifts.

Avoid degrading user experience.

---

# CMS Performance

Large CMS tables should use:

Pagination

Server-side filtering

Indexed search

Bulk operations

Lazy loading

Never render thousands of rows on one page.

---

# Search Performance

Search should remain fast even with large datasets.

Support efficient indexing.

Prepare architecture for future PostgreSQL Full Text Search or Elasticsearch integration.

Avoid scanning unnecessary records.

---

# Media Library Performance

Support:

Thumbnail generation

Progressive loading

Server-side filtering

Pagination

Folder navigation

Do not load the full media library into memory.

---

# API Performance

AJAX endpoints should:

Return only required data.

Avoid large payloads.

Support pagination where appropriate.

Compress responses when supported by the server.

---

# Compression

Enable server compression.

Recommended:

Gzip

Brotli (preferred when available)

Compress:

HTML

CSS

JavaScript

SVG

JSON

Do not compress already compressed formats unnecessarily.

---

# HTTP Caching

Configure browser caching appropriately.

Examples:

Images

CSS

JavaScript

Fonts

Use cache versioning for updates.

---

# Content Delivery

The architecture should allow future CDN integration.

Examples:

Cloudflare

Amazon CloudFront

Bunny CDN

The application should not require structural changes for CDN adoption.

---

# Memory Usage

Avoid unnecessary memory allocation.

Release temporary objects when appropriate.

Keep long-running background tasks memory-efficient.

---

# Scalability

The application should scale horizontally.

Avoid storing application state in memory.

Use Redis for shared caching and task queues.

Keep services stateless whenever practical.

---

# Monitoring

The architecture should support future monitoring.

Examples:

Application metrics

Slow query detection

Task monitoring

Error tracking

Performance dashboards

Monitoring should require minimal integration effort.

---

# SEO Performance

Performance contributes directly to SEO.

Optimize:

Core Web Vitals

Page speed

Image delivery

Structured HTML

Server response times

Maintain excellent search engine performance.

---

# Production Optimization

Before deployment:

Disable DEBUG.

Collect static files.

Minify assets.

Verify caching.

Optimize database indexes.

Test Lighthouse scores.

Confirm background workers are operational.

---

# Performance Testing

Test under realistic load.

Verify:

Homepage

Article pages

CMS

Media uploads

Search

Scheduled publishing

Performance should remain stable as traffic increases.

---

# Future Optimization

Architecture should support future enhancements.

Examples:

Edge caching

Image CDN

Object storage

Read replicas

Search clusters

Queue scaling

No major architectural redesign should be required.

---

# Final Performance Rule

Every implementation must consider performance before writing code.

Fast code is preferred.

Efficient queries are mandatory.

Background processing should handle expensive operations.

The project should remain responsive under high traffic and large datasets.

Performance is not an optimization phase.

Performance is a permanent development requirement.
# CLAUDE.md

# Chapter 14 — SEO, News Publishing & Content Standards

## General Philosophy

The website is a professional news portal.

Every article must be optimized for:

* Search engines
* Social media
* Fast indexing
* Readability
* User engagement

SEO is part of the architecture, not an optional feature.

Every page should be discoverable, indexable and properly structured.

---

# SEO Architecture

Every public page must include:

* Unique Title
* Meta Description
* Canonical URL
* Open Graph Tags
* Twitter/X Card Tags
* Structured Data
* Breadcrumb Schema
* Robots Directives

SEO metadata should be generated dynamically.

---

# HTML Metadata

Every page should generate:

```html id="u7n4bz"
<title></title>

<meta name="description">

<meta property="og:title">

<meta property="og:description">

<meta property="og:image">

<meta property="og:url">

<meta name="robots">

<link rel="canonical">
```

Never duplicate metadata across unrelated pages.

---

# URL Structure

URLs must remain short and readable.

Examples:

/

news/president-visits-baku/

category/politics/

category/technology/artificial-intelligence/

tag/economy/

search/

archive/

contact/

about/

Avoid unnecessary URL parameters.

Never expose database IDs in public URLs.

---

# Slug Rules

Slugs should:

Be lowercase.

Use hyphens.

Avoid special characters.

Remain human-readable.

Be editable before publishing.

Automatically generate when possible.

---

# XML Sitemap

Generate XML Sitemap automatically.

Include:

Homepage

Articles

Categories

Tags

Static Pages

Exclude:

CMS

Login

Draft Articles

Private Pages

Deleted Content

Sitemap should update automatically after content changes.

---

# Robots.txt

Generate robots.txt dynamically.

Allow indexing of public content.

Block:

CMS

Admin

Private Media

Temporary URLs

Development endpoints

---

# Canonical URLs

Every indexable page must define a canonical URL.

Avoid duplicate content.

Paginated pages should use appropriate canonical strategies.

---

# Open Graph

Generate Open Graph metadata automatically.

Include:

Title

Description

Image

URL

Site Name

Type

Locale

Open Graph images should use optimized WebP versions when appropriate.

---

# Twitter/X Cards

Support Twitter/X Card metadata.

Include:

Card Type

Title

Description

Image

Ensure attractive previews when shared.

---

# Structured Data

Use JSON-LD.

Support:

NewsArticle

BreadcrumbList

Organization

WebSite

ImageObject

SearchAction

Future support:

FAQ

VideoObject

LiveBlogPosting

Structured data should validate without errors.

---

# Article Metadata

Each article contains:

Title

Slug

Excerpt

Content

Featured Image

Category

Subcategory

Tags

Author

Publication Date

Last Updated

Reading Time

View Count

Status

SEO Metadata

Every field should have a clear purpose.

---

# Publication Workflow

Supported workflow:

Draft

↓

Pending Review

↓

Scheduled

↓

Published

↓

Archived

Articles should never skip workflow rules without authorization.

---

# Scheduled Publishing

Editors may schedule articles.

Celery should publish articles automatically.

Scheduled content should become visible immediately after publication time.

---

# Breaking News

Articles may be marked as:

Breaking News

Breaking News should:

Display badge.

Appear in breaking ticker.

Receive visual priority.

Support automatic expiration if configured.

---

# Featured Articles

Editors may mark articles as Featured.

Featured articles appear:

Homepage

Category pages

Related content

Featured status should be manageable from the CMS.

---

# Related Articles

Generate related articles based on:

Category

Tags

Manual selection

Related content improves navigation and engagement.

---

# Reading Time

Estimate reading time automatically.

Update after article edits.

Display beside publication metadata.

---

# View Counter

Track article views.

Prevent obvious duplicate counting.

Architecture should allow future bot filtering.

View counting should not slow page rendering.

---

# Search Engine Indexing

Only Published articles should be indexable.

Drafts

Scheduled Articles

Archived Content

Private Pages

must not be indexed.

---

# Pagination SEO

Category pages

Tag pages

Archive pages

must support SEO-friendly pagination.

Avoid duplicate content issues.

---

# Internal Linking

Encourage internal links between:

Articles

Categories

Tags

Related content

Static pages

Internal linking should improve navigation naturally.

---

# Image SEO

Every image supports:

Alt Text

Caption

Description (optional)

Optimized filename

WebP format

Responsive sizes

Images should contribute to SEO.

---

# Breadcrumbs

Every article displays breadcrumb navigation.

Example:

Home

↓

Politics

↓

International

↓

Article

Breadcrumbs should generate structured data automatically.

---

# Search

Website search supports:

Articles

Categories

Tags

Search results should remain indexable only when appropriate.

---

# Archive

Provide archive pages by:

Year

Month

Archive pages should remain SEO-friendly.

---

# 404 Optimization

Custom 404 page should include:

Search

Popular Articles

Categories

Homepage Link

Users should recover easily from broken links.

---

# Content Quality

Encourage editors to provide:

Clear titles

Readable paragraphs

Meaningful headings

Optimized excerpts

Relevant images

Avoid duplicate content.

---

# Social Sharing

Support sharing to:

Facebook

X (Twitter)

LinkedIn

Telegram

WhatsApp

Copy Link

Sharing should use generated Open Graph metadata.

---

# Future SEO Expansion

Architecture should support:

Google News

AMP (if ever required)

Video Articles

Live Blogs

Author Pages

Topic Pages

RSS Feeds

Newsletters

AI-generated summaries

without major redesign.

---

# Analytics Readiness

Architecture should allow integration with:

Google Analytics

Google Search Console

Microsoft Clarity

Meta Pixel

Custom analytics

Tracking scripts should be configurable from the CMS.

---

# Final SEO Rule

Every public page must be technically optimized before publication.

SEO should be automatic wherever possible.

Editors should focus on content, while the system handles technical optimization.

The website should be capable of achieving excellent search engine visibility through clean architecture, structured data and fast performance.
# CLAUDE.md

# Chapter 15 — Coding Standards, Code Quality & AI Development Rules

## General Philosophy

This project is intended to become a long-term commercial product.

Every line of code must be written as production-quality software.

Temporary solutions, shortcuts and experimental implementations are strictly prohibited.

The objective is not only to make the application work, but to build a codebase that remains clean, understandable and maintainable for many years.

Code quality always takes priority over development speed.

---

# AI Development Principles

Claude Code is the primary development assistant for this project.

Every generated file must follow the architectural standards defined in this document.

Claude must never generate demo-quality code.

Claude must never sacrifice architecture for convenience.

When multiple implementation approaches exist, always choose the solution that best aligns with:

* Simplicity
* Maintainability
* Performance
* Security
* Scalability

---

# Before Writing Code

Before implementing any feature Claude must:

1. Understand the feature completely.

2. Review the existing architecture.

3. Reuse existing components whenever possible.

4. Avoid creating duplicate functionality.

5. Plan the implementation before generating code.

Code generation should never begin without understanding the surrounding architecture.

---

# File Creation Rules

Before creating a new file Claude must verify:

Does a similar file already exist?

Can an existing component be extended?

Will this introduce duplication?

New files should only be created when necessary.

Avoid unnecessary project growth.

---

# Refactoring Rules

Claude should continuously improve code quality.

If existing code can be simplified without changing behavior:

Refactor it.

Remove duplication.

Improve naming.

Reduce complexity.

Preserve compatibility.

Refactoring should improve maintainability without introducing unnecessary architectural changes.

---

# Naming Standards

Names must clearly describe intent.

Variables:

camelCase (JavaScript)

snake_case (Python fields where appropriate)

Classes:

PascalCase

Constants:

UPPER_CASE

Functions:

Descriptive verb-based names.

Examples:

publishArticle()

generateThumbnail()

optimizeImage()

archiveNews()

Avoid vague names.

Examples to avoid:

run()

temp()

data()

test()

item()

---

# Function Design

Functions should perform one task.

Prefer small functions.

Avoid deeply nested logic.

Break complex operations into reusable helper methods or services.

Functions should be easy to understand without extensive comments.

---

# Class Design

Classes should follow the Single Responsibility Principle.

Avoid "God Classes".

Large classes should be divided into focused services or components.

Every public method should have a clear purpose.

---

# DRY Principle

Do not Repeat Yourself.

Never duplicate:

Business logic

SQL queries

Validation

Templates

CSS

JavaScript

Configuration

If duplication appears, extract a reusable solution.

---

# SOLID Principles

Implement SOLID principles whenever practical.

Especially:

Single Responsibility

Open/Closed

Dependency Inversion

Avoid unnecessary abstraction.

Apply SOLID pragmatically.

---

# Readability

Code should read like documentation.

Prioritize clarity over cleverness.

Future developers should understand code quickly.

Readable code is more valuable than short code.

---

# Comments

Comments explain:

Why something exists.

Why a decision was made.

Why an implementation differs from the obvious solution.

Comments should not explain obvious syntax.

Avoid commented-out code.

Remove obsolete comments during refactoring.

---

# Error Handling

Handle errors explicitly.

Never ignore exceptions.

Provide useful logging.

Return meaningful user-facing messages.

Unexpected failures should never crash the application.

---

# Logging

Important operations should produce structured logs.

Avoid excessive logging.

Never log:

Passwords

Tokens

Secrets

Personal sensitive information

Logs should assist debugging without compromising security.

---

# Configuration

Hardcoded configuration is forbidden.

Configuration belongs in:

Environment variables

Settings

Configuration modules

Never hardcode URLs, credentials or environment-specific values.

---

# Dependencies

Before installing a dependency Claude must determine:

Is it actively maintained?

Does Django already provide this functionality?

Can the feature be implemented without another package?

Avoid dependency bloat.

---

# Third-Party Libraries

Every external package must provide clear value.

Remove abandoned libraries.

Avoid packages with poor maintenance history.

Prefer standard Django solutions whenever possible.

---

# Git Standards

Every logical change should be committed separately.

Commit messages should be meaningful.

Examples:

Add article scheduling

Implement media cropper

Optimize homepage queries

Avoid generic messages such as:

Update

Fix

Changes

Work

---

# Documentation

Complex modules should include concise documentation.

Architecture decisions should be documented.

Public services should have clear docstrings where appropriate.

Documentation should remain synchronized with implementation.

---

# Testing Readiness

Although automated testing may be added later, code must always be testable.

Avoid tightly coupled implementations.

Prefer dependency injection where appropriate.

Keep side effects isolated.

---

# Code Review Checklist

Before considering work complete Claude should verify:

Architecture is respected.

No duplicated logic exists.

Naming is consistent.

Performance is acceptable.

Security has been considered.

Accessibility has not been broken.

Responsive behavior remains intact.

Code formatting is consistent.

Unused imports are removed.

Dead code is removed.

Temporary debugging code is removed.

---

# Forbidden Practices

Never:

Create duplicate components.

Write inline CSS.

Write inline JavaScript.

Duplicate templates.

Mix business logic with presentation.

Ignore validation.

Ignore permission checks.

Leave TODO comments without explicit approval.

Leave placeholder implementations.

Commit experimental code.

Reduce quality to save time.

---

# Development Workflow

For every new feature Claude should follow this sequence:

Understand the requirement.

↓

Analyze existing architecture.

↓

Design the implementation.

↓

Reuse existing components.

↓

Write clean code.

↓

Verify responsiveness.

↓

Verify accessibility.

↓

Verify performance.

↓

Verify security.

↓

Refactor if necessary.

↓

Deliver production-ready implementation.

---

# Definition of Done

A task is complete only when:

The feature works correctly.

Architecture remains clean.

Code follows project standards.

No duplication exists.

Performance is acceptable.

Security has been verified.

Responsive behavior works.

Accessibility has been maintained.

No unnecessary files were created.

No technical debt was introduced.

---

# Long-Term Maintainability

Claude should always optimize for future developers.

Every implementation should remain understandable after several years.

Avoid clever solutions that reduce readability.

The project should remain easy to extend without major refactoring.

---

# Final Development Rule

Claude Code must behave as a senior software architect, senior Django engineer and senior frontend engineer simultaneously.

Every generated solution must be production-ready.

Every architectural decision must support long-term commercial maintenance.

Quality is never optional.

Maintainability is never optional.

Security is never optional.

Performance is never optional.

The objective is to build a professional news platform whose codebase reflects enterprise-level engineering standards from the very first commit.
