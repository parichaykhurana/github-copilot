import pytest


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_for_activity(self, client, reset_activities):
        """Test signing up for an activity"""
        email = "netstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test signing up for an activity when already signed up"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_activity_not_found(self, client):
        """Test signing up for a non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_special_characters_in_email(self, client, reset_activities):
        """Test signing up with special characters in email"""
        email = "test+student@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email in client.get("/activities").json()[activity]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestParticipantsData:
    """Test participant data integrity"""
    
    def test_initial_participants_exist(self, client):
        """Test that initial participants are present"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check specific initial participants
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "john@mergington.edu" in activities["Gym Class"]["participants"]
    
    def test_activity_capacity_info(self, client):
        """Test that capacity information is present"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity in activities.values():
            assert activity["max_participants"] > 0
            assert len(activity["participants"]) <= activity["max_participants"]
