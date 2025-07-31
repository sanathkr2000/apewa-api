# tests/test_jobs.py
import pytest
from fastapi import status
from httpx import AsyncClient
# Example job to use in mocking or inserts
example_job = {
    "job_id": 1,
    "job_title": "Software Engineer",
    "company": "Tech Corp",
    "location": "New York",
    "description": "Develop software applications.",
    "requirements": "Python, FastAPI"
}


@pytest.mark.anyio
async def test_create_job_success(async_client):
    payload = {
  "job_title": "Angular Developer",
  "company": "New Inc.",
  "location": "Texas, CA",
  "job_type": "contract",
  "description": "looking for a angular developer who have 4 years of experiance",
  "requirements": [
    "3+ years of experience with Angular",
    "Proficiency in HTML, CSS, and JavaScript",
    "Experience with RESTful APIs",
    "Familiarity with version control systems (e.g., Git)",
    "Strong problem-solving and debugging skills"
  ],
  "salary_range": "$10,000 - $13,000 USD/year",
  "website": "https://www.new.io/careers",
  "remote": True,
  "active": True,
  "visatype": "H1B,CPT",
  "employer_id": 102,
  "status":"Draft",
  "created_at": "2025-07-24T07:19:30.673Z"
}


    response = await async_client.post("/jobs/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["job_title"] == payload["job_title"]
    assert data["description"] == payload["description"]
    assert "job_id" in data

@pytest.mark.anyio
async def test_get_all_jobs(async_client: AsyncClient):
    response = await async_client.get("/jobs")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_job_by_id_found(async_client: AsyncClient):
    response = await async_client.get("/jobs/1")
    if response.status_code == 200:
        job = response.json()
        assert "job_title" in job
    else:
        assert response.status_code == 404


@pytest.mark.anyio
async def test_get_job_by_id_not_found(async_client: AsyncClient):
    response = await async_client.get("/jobs/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"