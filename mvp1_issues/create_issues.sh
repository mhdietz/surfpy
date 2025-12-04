#!/bin/bash

# Create Parent Issue 1: Comments System
PARENT_1=$(gh issue create \
  --title "[MVP_1] Comments System" \
  --body-file parent_comments.md \
  --label "P0-MVP,feature" \
  --assignee stefanoscotti \
  | grep -oP '(?<=issues/)\d+')

echo "Created Parent Issue #$PARENT_1"

# Create Sub-issues for Comments
gh issue create \
  --title "[MVP_1][Comments] Backend: Comments table and API endpoints" \
  --body-file comments_backend.md \
  --label "P0-MVP,backend,stefanoscotti" \
  --assignee stefanoscotti

gh issue create \
  --title "[MVP_1][Comments] Frontend: CommentModal component" \
  --body-file comments_modal.md \
  --label "P0-MVP,frontend,stefanoscotti" \
  --assignee stefanoscotti

gh issue create \
  --title "[MVP_1][Comments] Frontend: Add comment UI to tiles and detail view" \
  --body-file comments_ui.md \
  --label "P0-MVP,frontend,stefanoscotti" \
  --assignee stefanoscotti

# Create Parent Issue 2: Surf Spots
PARENT_2=$(gh issue create \
  --title "[MVP_1] Expanded Surf Spots with Typeahead Search" \
  --body-file parent_spots.md \
  --label "P0-MVP,feature" \
  --assignee mhdietz \
  | grep -oP '(?<=issues/)\d+')

echo "Created Parent Issue #$PARENT_2"

# Create Sub-issues for Surf Spots
gh issue create \
  --title "[MVP_1][Spots] Backend: Schema updates and import script" \
  --body-file spots_backend_schema.md \
  --label "P0-MVP,backend,mhdietz" \
  --assignee mhdietz

gh issue create \
  --title "[MVP_1][Spots] Backend: Curate spots and run import" \
  --body-file spots_backend_import.md \
  --label "P0-MVP,backend,mhdietz" \
  --assignee mhdietz

gh issue create \
  --title "[MVP_1][Spots] Frontend: Typeahead component" \
  --body-file spots_frontend_typeahead.md \
  --label "P0-MVP,frontend,mhdietz" \
  --assignee mhdietz

gh issue create \
  --title "[MVP_1][Spots] Frontend: Handle missing surf data" \
  --body-file spots_frontend_no_data.md \
  --label "P0-MVP,frontend,mhdietz" \
  --assignee mhdietz

# Create Issue 3: Sticky Feed
gh issue create \
  --title "[MVP_1] Sticky Feed Position (Scroll Persistence)" \
  --body-file sticky_feed.md \
  --label "P1-MVP,frontend,mhdietz" \
  --assignee mhdietz

echo "All issues created!"