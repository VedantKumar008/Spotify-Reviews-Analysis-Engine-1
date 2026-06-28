# Problem Statement

I want to build an AI-powered review analysis workflow focused on Spotify user reviews.

The purpose of the application is to demonstrate how user feedback can be transformed into actionable product insights using AI. The application should use real review data and generate concise answers to predefined research questions.

## Core Objective

The system should analyze a large dataset of Spotify reviews collected from Google Play and identify recurring user problems, behaviors, frustrations, and unmet needs related to music discovery and recommendations.

## Data Requirements

* Use real Spotify reviews from Google Play.
* The dataset should contain approximately 10,000 reviews.
* Reviews should prioritize recency and relevance.
* The dataset should be cleaned before analysis to remove noise, duplicates, spam, and low-value content.
* The same processed dataset can be reused for all workflow executions after deployment to ensure reliability and fast performance.

## Landing Page Requirements

The landing page should be intentionally simple and should visually represent the workflow at a high level.

The page should contain three horizontally aligned workflow boxes:

1. Reviews Ingestion
2. Data Cleaning
3. LLM Analysis

The page should not expose technical implementation details.

Below the workflow visualization there should be a prominent "Run Workflow" button.

The purpose of this page is to help users immediately understand the overall flow of the system before running the analysis.

## Workflow Execution Experience

When the user clicks "Run Workflow", they should be taken to a separate results page.

The workflow should appear to execute and then present the final insights generated from the analyzed review dataset.

## Results Page Requirements

The results page should display answers to the following six predefined research questions:

1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

## Answer Requirements

* Each answer should be concise.
* Answers should be limited to approximately 3–4 lines.
* Answers must be generated from the analyzed review dataset rather than hardcoded text.
* The focus should be on clear product insights rather than technical analysis.

## User Experience Requirements

* Clean and professional interface.
* Easy for a mentor or evaluator to understand and test.
* Fast workflow execution experience.
* No login or authentication required.
* Suitable for deployment and sharing through a public URL.

## Success Criteria

A user visiting the deployed application should be able to:

1. Understand the review analysis workflow from the landing page.
2. Run the workflow with a single click.
3. View AI-generated answers to the six predefined research questions.
4. Clearly see that the insights are derived from real Spotify review data.
