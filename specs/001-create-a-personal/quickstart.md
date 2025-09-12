# Quickstart Guide: Personal Blog Platform

## Overview
This quickstart guide validates the core user stories from the feature specification by walking through the main user flows. It serves as both documentation and integration test scenarios.

## Prerequisites
- Python 3.11+ installed
- Node.js 18+ and npm installed  
- PostgreSQL 14+ running locally
- Git for version control

## Setup Instructions

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd AIBlogEditor

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your database credentials

# Database setup
createdb blog_db  # PostgreSQL command
alembic upgrade head  # Run migrations

# Frontend setup
cd ../frontend
npm install
```

### 2. Start Development Servers
```bash
# Terminal 1: Backend (Priority per user requirement)
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend  
npm run dev
```

## User Story Validation

### Story 1: Homepage with Featured Content
**Given**: A new visitor  
**When**: They access the blog at `http://localhost:5173`  
**Then**: They should see:

- [ ] Modern, polished UI with professional styling
- [ ] Homepage displaying featured writing and projects
- [ ] Clean, readable layout with proper visual hierarchy
- [ ] Responsive design on different screen sizes

**Validation Steps**:
1. Open browser to `http://localhost:5173`
2. Verify homepage loads with modern styling
3. Check that blog posts are displayed if any exist
4. Check that projects are displayed if any exist
5. Resize browser to test responsive behavior
6. Validate loading states and error handling

### Story 2: Content Readability and Navigation  
**Given**: A user browsing the blog  
**When**: They read an article or view a project  
**Then**: Content should be presented with high readability

**Validation Steps**:
1. Navigate to a blog post: `http://localhost:5173/posts/{slug}`
2. Verify:
   - [ ] Clean typography and proper spacing
   - [ ] Readable font sizes and line heights
   - [ ] Good contrast ratios for accessibility
   - [ ] Proper content hierarchy (headings, paragraphs)
   - [ ] Navigation elements are clear and functional

### Story 3: MVP Functionality Without AI Features
**Given**: The MVP release  
**When**: AI features are not yet present  
**Then**: The blog should function fully for reading and browsing

**Validation Steps**:
1. Verify all core features work without AI dependencies:
   - [ ] Blog post listing and individual post viewing
   - [ ] Project listing and individual project viewing
   - [ ] Tag-based filtering
   - [ ] Search functionality (basic text search)
   - [ ] Admin interface for content management

### Story 4: Future AI Feature Compatibility
**Given**: Future updates with AI features  
**When**: AI features are enabled  
**Then**: They should enhance without disrupting core functionality

**Validation Steps** (for future reference):
1. Ensure architecture supports AI feature integration:
   - [ ] Tag system ready for AI-powered tagging
   - [ ] Content structure supports spellcheck integration
   - [ ] Search infrastructure can accommodate AI finder agent
   - [ ] UI components can handle additional AI-powered features

## API Validation

### Authentication Flow
```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Expected: 200 OK with access_token and user profile
```

### Blog Post Operations
```bash
# List published posts
curl http://localhost:8000/api/v1/posts

# Get specific post
curl http://localhost:8000/api/v1/posts/my-first-post

# Create new post (requires authentication)
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Post", "content": "Test content"}'
```

### Project Operations
```bash
# List published projects
curl http://localhost:8000/api/v1/projects

# Get specific project
curl http://localhost:8000/api/v1/projects/my-awesome-project

# Create new project (requires authentication)
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Project", "description": "A test project description"}'
```

## Edge Case Testing

### Empty Content Scenarios
1. **No blog posts exist**:
   - [ ] Homepage shows appropriate "No posts yet" message
   - [ ] Message includes call-to-action for admin users
   - [ ] Layout remains visually appealing with empty state

2. **No projects exist**:
   - [ ] Projects section shows appropriate empty state
   - [ ] Design maintains visual balance

### Responsive Design Testing
1. **Mobile devices** (320px - 768px):
   - [ ] Navigation collapses to mobile menu
   - [ ] Content remains readable without horizontal scroll
   - [ ] Touch targets are appropriately sized

2. **Tablet devices** (768px - 1024px):
   - [ ] Layout adapts properly to medium screens
   - [ ] Content maintains proper proportions

3. **Large screens** (1024px+):
   - [ ] Content doesn't stretch uncomfortably wide
   - [ ] Proper use of whitespace

### Performance Testing
1. **Page load times**:
   - [ ] Homepage loads in < 500ms (local development)
   - [ ] Individual posts load in < 300ms
   - [ ] API responses return in < 200ms

2. **Network conditions**:
   - [ ] Graceful loading states for slow connections
   - [ ] Progressive enhancement for poor network
   - [ ] Error handling for network failures

## Database Validation

### Data Integrity
```sql
-- Verify required tables exist
\dt

-- Check constraints and indexes
\d blog_posts
\d projects  
\d users
\d tags

-- Test data relationships
SELECT bp.title, u.username, array_agg(t.name) as tags
FROM blog_posts bp
JOIN users u ON bp.author_id = u.id
LEFT JOIN blog_post_tags bpt ON bp.id = bpt.blog_post_id
LEFT JOIN tags t ON bpt.tag_id = t.id
GROUP BY bp.id, u.username;
```

### Migration Testing
```bash
# Test migration rollback and upgrade
alembic downgrade -1
alembic upgrade head

# Verify data consistency after migrations
python -c "
from database import SessionLocal
from models import BlogPost, User, Project
db = SessionLocal()
print('Posts:', db.query(BlogPost).count())
print('Users:', db.query(User).count())
print('Projects:', db.query(Project).count())
db.close()
"
```

## Security Validation

### Authentication Security
- [ ] Passwords are properly hashed (bcrypt)
- [ ] JWT tokens expire appropriately
- [ ] Refresh token rotation works
- [ ] CSRF protection is enabled

### Input Validation
- [ ] SQL injection prevention via ORM
- [ ] XSS prevention in content rendering
- [ ] File upload restrictions (if applicable)
- [ ] Rate limiting on API endpoints

## Completion Checklist

### Backend Requirements
- [ ] All API endpoints respond correctly
- [ ] Database schema matches data model
- [ ] Authentication system works
- [ ] Input validation is comprehensive
- [ ] Error handling provides useful feedback

### Frontend Requirements  
- [ ] Modern, polished UI matches design requirements
- [ ] All pages render correctly
- [ ] Navigation works smoothly
- [ ] Responsive design functions properly
- [ ] Loading states and error handling

### Integration Requirements
- [ ] Frontend successfully communicates with backend
- [ ] API contract matches OpenAPI specification
- [ ] End-to-end user flows work seamlessly
- [ ] Performance targets are met

## Next Steps After Quickstart
1. Set up automated testing pipeline
2. Configure production deployment
3. Implement content migration if needed
4. Plan AI feature integration architecture
5. Set up monitoring and logging

---
*This quickstart guide serves as both documentation and acceptance criteria for the personal blog platform*