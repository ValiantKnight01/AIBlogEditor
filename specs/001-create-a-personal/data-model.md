# Data Model Design

## Core Entities

### User Entity
**Purpose**: Represents the blog owner with authentication and profile information.

**Fields**:
- `id`: UUID (Primary Key)
- `email`: String, unique, required (authentication identifier)
- `username`: String, unique, required (public identifier)  
- `password_hash`: String, required (bcrypt hashed)
- `full_name`: String, optional (display name)
- `bio`: Text, optional (author bio for about page)
- `avatar_url`: String, optional (profile image URL)
- `is_active`: Boolean, default True (account status)
- `created_at`: DateTime, auto-generated
- `updated_at`: DateTime, auto-updated

**Relationships**:
- One-to-many with BlogPost (author)
- One-to-many with Project (creator)

**Validation Rules**:
- Email must be valid format
- Username: 3-50 characters, alphanumeric + underscore
- Bio: max 500 characters
- Password: minimum 8 characters (enforced at API level)

### BlogPost Entity  
**Purpose**: Represents individual blog articles with content and metadata.

**Fields**:
- `id`: UUID (Primary Key)
- `title`: String, required, max 200 characters
- `slug`: String, unique, required (URL-friendly identifier)
- `content`: Text, required (Markdown format)
- `excerpt`: String, optional, max 300 characters (for previews)
- `status`: Enum ['draft', 'published'], default 'draft'
- `author_id`: UUID (Foreign Key to User)
- `published_at`: DateTime, optional (null for drafts)
- `created_at`: DateTime, auto-generated  
- `updated_at`: DateTime, auto-updated
- `view_count`: Integer, default 0
- `featured_image_url`: String, optional
- `meta_title`: String, optional (SEO title override)
- `meta_description`: String, optional (SEO description)

**Relationships**:
- Many-to-one with User (author)
- Many-to-many with Tag (through blog_post_tags table)

**Validation Rules**:
- Title: required, 5-200 characters
- Slug: auto-generated from title, must be unique
- Content: required, minimum 10 characters
- Published posts must have published_at timestamp

**State Transitions**:
- Draft → Published: Sets published_at timestamp
- Published → Draft: Clears published_at timestamp

### Project Entity
**Purpose**: Represents portfolio projects to showcase alongside blog content.

**Fields**:
- `id`: UUID (Primary Key)
- `title`: String, required, max 100 characters
- `slug`: String, unique, required
- `description`: Text, required (Markdown format)
- `short_description`: String, optional, max 200 characters
- `status`: Enum ['draft', 'published'], default 'draft'  
- `creator_id`: UUID (Foreign Key to User)
- `project_url`: String, optional (live project link)
- `github_url`: String, optional (source code link)
- `image_url`: String, optional (project screenshot)
- `tech_stack`: JSON, optional (array of technology names)
- `start_date`: Date, optional
- `end_date`: Date, optional
- `published_at`: DateTime, optional
- `created_at`: DateTime, auto-generated
- `updated_at`: DateTime, auto-updated

**Relationships**:
- Many-to-one with User (creator)
- Many-to-many with Tag (through project_tags table)

**Validation Rules**:
- Title: required, 5-100 characters
- Description: required, minimum 20 characters
- URLs: must be valid HTTP/HTTPS format if provided
- End date must be after start date if both provided

### Tag Entity
**Purpose**: Categorization system for blog posts and projects.

**Fields**:
- `id`: UUID (Primary Key)
- `name`: String, unique, required, max 50 characters
- `slug`: String, unique, required (URL-friendly)
- `color`: String, optional (hex color code for UI)
- `description`: String, optional, max 200 characters
- `created_at`: DateTime, auto-generated
- `post_count`: Integer, computed (number of associated posts)
- `project_count`: Integer, computed (number of associated projects)

**Relationships**:
- Many-to-many with BlogPost (through blog_post_tags)
- Many-to-many with Project (through project_tags)

**Validation Rules**:
- Name: required, 2-50 characters, alphanumeric + spaces
- Color: must be valid hex color if provided
- Case-insensitive uniqueness on name

## Junction Tables

### blog_post_tags
**Purpose**: Many-to-many relationship between BlogPost and Tag

**Fields**:
- `blog_post_id`: UUID (Foreign Key)
- `tag_id`: UUID (Foreign Key)
- `created_at`: DateTime

**Constraints**: Composite primary key (blog_post_id, tag_id)

### project_tags
**Purpose**: Many-to-many relationship between Project and Tag

**Fields**:
- `project_id`: UUID (Foreign Key)
- `tag_id`: UUID (Foreign Key)  
- `created_at`: DateTime

**Constraints**: Composite primary key (project_id, tag_id)

## Database Indexes

**Performance-Critical Indexes**:
- `blog_posts.slug` (unique index for fast lookup)
- `blog_posts.status` (for published post queries)
- `blog_posts.published_at` (for chronological ordering)
- `blog_posts.author_id` (for author-specific queries)
- `projects.slug` (unique index for fast lookup)
- `projects.status` (for published project queries)
- `tags.slug` (unique index for fast lookup)
- `users.email` (unique index for authentication)
- `users.username` (unique index for public lookups)

**Composite Indexes**:
- `(blog_posts.status, blog_posts.published_at)` for published post listings
- `(projects.status, projects.created_at)` for published project listings

## Future Enhancements (Not MVP)

### Comment Entity (for AI features later)
- Support for user comments on blog posts
- Moderation workflow
- Reply threading

### Analytics Entity (for AI features later)  
- Page view tracking
- User behavior analysis
- Popular content identification

### Media Entity (for rich content)
- File upload management
- Image optimization
- Gallery support

---
*Data model supports all functional requirements from feature specification*