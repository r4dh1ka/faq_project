# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **YakshaBot AI Auto-Answer**: Integrated a RAG pipeline that automatically answers new community questions instantly using the FAQ knowledge base.
- **Reddit-Style Threaded Q&A**: Upgraded the simple Q&A layout to a fully recursive, infinitely nestable tree structure.
- **Interactive Threadlines**: Added hover-illuminating vertical threadlines to visually track deeply nested comments.
- **Minimalist Action Bars**: Replaced bulky buttons with a sleek Reddit-style inline action bar (Score, Reply, Share).

### Changed
- **Complete UI/UX Overhaul**: Upgraded from standard Bootstrap to a modern Glassmorphism design with a Deep Slate dark mode and glowing radial gradients.
- **High-Concurrency DB Optimization**: Optimized `qa/views.py` with `select_related` and `prefetch_related` to eliminate N+1 query bottlenecks and support 2000-3000 concurrent users.
- **Modern Typography**: Integrated Outfit and Inter web fonts for a premium SaaS aesthetic.
