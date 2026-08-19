"""
Integration tests for API endpoints.
Tests the complete flow: profile -> risk -> goal -> plan -> chat
"""

import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns app info."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "database" in data
    
    def test_api_info(self, client):
        """Test API info endpoint."""
        response = client.get("/api")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "endpoints" in data


class TestCustomerProfileAPI:
    """Test customer profile endpoints."""
    
    def test_create_customer_profile(self, client, sample_customer_data):
        """Test creating a customer profile."""
        response = client.post("/api/v1/profile/", json=sample_customer_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == sample_customer_data["name"]
        assert data["age"] == sample_customer_data["age"]
        assert "net_worth" in data
        assert "monthly_surplus" in data
        assert "debt_to_income_ratio" in data
        assert data["id"] > 0
    
    def test_get_customer_profile(self, client, sample_customer_data):
        """Test retrieving a customer profile."""
        # Create profile
        create_response = client.post("/api/v1/profile/", json=sample_customer_data)
        customer_id = create_response.json()["id"]
        
        # Get profile
        response = client.get(f"/api/v1/profile/{customer_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == customer_id
        assert data["name"] == sample_customer_data["name"]
    
    def test_get_nonexistent_profile(self, client):
        """Test getting a profile that doesn't exist."""
        response = client.get("/api/v1/profile/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_profiles(self, client, sample_customer_data):
        """Test listing all profiles."""
        # Create multiple profiles
        for i in range(3):
            data = sample_customer_data.copy()
            data["name"] = f"Customer {i}"
            client.post("/api/v1/profile/", json=data)
        
        # List profiles
        response = client.get("/api/v1/profile/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 3
    
    def test_financial_summary(self, client, sample_customer_data):
        """Test getting financial summary."""
        # Create profile
        create_response = client.post("/api/v1/profile/", json=sample_customer_data)
        customer_id = create_response.json()["id"]
        
        # Get summary
        response = client.get(f"/api/v1/profile/{customer_id}/summary")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "net_worth" in data
        assert "monthly_surplus" in data
        assert "financial_health_score" in data

    def test_another_user_cannot_access_profile(self, client, sample_customer_data):
        owner_token = client.headers["Authorization"]
        created = client.post("/api/v1/profile/", json=sample_customer_data)
        customer_id = created.json()["id"]

        other = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Other User",
                "email": "other@example.com",
                "password": "otherpass123",
            },
        )
        client.headers["Authorization"] = f"Bearer {other.json()['access_token']}"
        try:
            response = client.get(f"/api/v1/profile/{customer_id}")
            assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            client.headers["Authorization"] = owner_token


class TestRiskAssessmentAPI:
    """Test risk assessment endpoints."""
    
    def test_get_questionnaire(self, client):
        """Test getting risk questionnaire."""
        response = client.get("/api/v1/risk/questionnaire")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 10
    
    def test_create_risk_assessment(self, client, sample_customer_data, sample_risk_answers):
        """Test creating a risk assessment."""
        # Create customer first
        customer_response = client.post("/api/v1/profile/", json=sample_customer_data)
        customer_id = customer_response.json()["id"]
        
        # Create risk assessment
        assessment_data = {
            "customer_id": customer_id,
            "answers": sample_risk_answers
        }
        response = client.post("/api/v1/risk/", json=assessment_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["customer_id"] == customer_id
        assert "risk_score" in data
        assert data["risk_category"] in ["Conservative", "Moderate", "Aggressive"]


class TestCompleteFlow:
    """Test complete user flow from profile creation to plan generation."""
    
    def test_complete_workflow(self, client, sample_customer_data, sample_goal_data, sample_risk_answers):
        """Test the complete user journey."""
        # 1. Create customer profile
        customer_response = client.post("/api/v1/profile/", json=sample_customer_data)
        assert customer_response.status_code == status.HTTP_201_CREATED
        customer_id = customer_response.json()["id"]
        
        # 2. Submit risk assessment
        assessment_data = {
            "customer_id": customer_id,
            "answers": sample_risk_answers
        }
        risk_response = client.post("/api/v1/risk/", json=assessment_data)
        assert risk_response.status_code == status.HTTP_201_CREATED
        
        # 3. Create financial goal
        goal_data = {**sample_goal_data, "customer_id": customer_id}
        goal_response = client.post("/api/v1/goal/", json=goal_data)
        assert goal_response.status_code == status.HTTP_201_CREATED
        goal_id = goal_response.json()["id"]
        
        # 4. Generate financial plans
        plan_request = {
            "customer_id": customer_id,
            "goal_ids": [goal_id],
            "custom_parameters": {"monthly_investment": 1_000},
        }
        plans_response = client.post("/api/v1/plans/generate", json=plan_request)
        assert plans_response.status_code == status.HTTP_200_OK
        plans = plans_response.json()
        assert len(plans) == 3
        assert all(plan["monthly_investment"] == 1_000 for plan in plans)
        assert all(plan["total_planned_contributions"] == 300_000 for plan in plans)
        
        # Verify complete flow
        assert customer_id > 0
        assert goal_id > 0
        assert len(plans) == 3
