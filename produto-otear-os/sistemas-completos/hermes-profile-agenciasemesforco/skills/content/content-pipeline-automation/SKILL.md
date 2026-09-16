---
name: content-pipeline-automation
description: |
  Skills for automating end-to-end content workflows, from data acquisition and filtering
  to task management and downstream content processing. This umbrella skill aggregates
  specialized tools for various content pipeline needs.
category: content
---

# Content Pipeline Automation

This skill collection manages automated workflows for content creation and distribution pipelines. It consolidates tools for data sourcing, filtering, task creation, and downstream processing.

## News Monitoring and Content Ideation
Sub-skills in this category focus on gathering and processing information to fuel content production.

### News Monitoring Pipeline
Provides a detailed workflow for monitoring AI/tech news, filtering for video potential, and integrating with task management systems like ClickUp.
- **Core Functionality:** Aggregates RSS and HTML feeds for AI/tech news, filters articles based on AI keywords and video-related triggers, and creates tasks in ClickUp for content teams.
- **Key Features:** Supports multiple news sources (Hacker News, TechCrunch AI, Hugging Face Blog, arXiv CS.AI), configurable recency and relevance filters, and direct task creation with specific naming conventions and descriptions.
- **Linked Content:** The `news-monitoring-pipeline` skill (category: `content`) contains the specific implementation scripts (`scripts/fetch_news.py`, `scripts/push_clickup.py`), configuration (`templates/config.yaml`), and detailed reference guides (`references/`). The full original skill can be viewed with `skill_view(name='news-monitoring-pipeline', category='content')`.
