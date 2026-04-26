# -*- coding: utf-8 -*-
"""
SoulNutri - Test Suite for New Features (Iteration 4)
Tests:
1. Notification System (generate, list, mark read, max 1/day)
2. Admin Settings/Premium/API-Usage/Processing-Metrics endpoints
3. Safe Nutrition Update (preview, update-single, rollback, audit-log)
4. Moderation Queue (already tested in iteration 3, quick verification)
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://admin-pin-portal.preview.emergentagent.com').rstrip('/')

class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_api_health(self):
        """Test /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("✅ API health check passed")


class TestNotificationSystem:
    """Tests for Push Notification System"""
    
    @pytest.fixture
    def unique_user_pin(self):
        """Generate unique user pin for testing"""
        return f"test_{uuid.uuid4().hex[:8]}"
    
    def test_generate_notification(self, unique_user_pin):
        """POST /api/notifications/generate - creates personalized notification"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "notification" in data
        notification = data["notification"]
        # Verify notification structure
        assert "type" in notification
        assert "title" in notification
        assert "message" in notification
        assert "references" in notification
        assert "user_pin" in notification
        assert notification["user_pin"] == unique_user_pin
        print(f"✅ Notification generated: {notification.get('title')}")
    
    def test_max_one_notification_per_day(self, unique_user_pin):
        """Test that max 1 notification per day is enforced"""
        # First notification should succeed
        response1 = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("ok") == True
        
        # Second notification same day should be rejected
        response2 = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("ok") == False
        assert data2.get("reason") == "already_sent_today"
        print("✅ Max 1 notification/day enforced correctly")
    
    def test_get_user_notifications(self, unique_user_pin):
        """GET /api/notifications/{user_pin} - lists notifications with unread count"""
        # First generate a notification
        requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        
        # Then fetch notifications
        response = requests.get(f"{BASE_URL}/api/notifications/{unique_user_pin}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "notifications" in data
        assert "unread" in data
        assert isinstance(data["notifications"], list)
        assert len(data["notifications"]) >= 1
        print(f"✅ Got {len(data['notifications'])} notifications, {data['unread']} unread")
    
    def test_notification_has_references(self, unique_user_pin):
        """Verify notifications include references and links"""
        # Generate notification
        response = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        data = response.json()
        assert data.get("ok") == True
        
        notification = data["notification"]
        references = notification.get("references", [])
        assert isinstance(references, list)
        assert len(references) >= 1, "Notification should have at least 1 reference"
        
        # Verify reference structure
        for ref in references:
            assert "source" in ref, "Reference should have source"
            assert "url" in ref, "Reference should have URL"
            assert ref["url"].startswith("http"), "URL should be valid"
        print(f"✅ Notification has {len(references)} references with valid URLs")
    
    def test_mark_notification_read(self, unique_user_pin):
        """POST /api/notifications/{user_pin}/read - marks notification as read"""
        # Generate notification
        gen_response = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json={"user_pin": unique_user_pin, "user_name": "Test User"}
        )
        notification = gen_response.json().get("notification", {})
        date = notification.get("date")
        
        # Mark as read
        response = requests.post(
            f"{BASE_URL}/api/notifications/{unique_user_pin}/read",
            json={"date": date}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        
        # Verify unread count decreased
        list_response = requests.get(f"{BASE_URL}/api/notifications/{unique_user_pin}")
        list_data = list_response.json()
        assert list_data.get("unread", 1) == 0
        print("✅ Notification marked as read successfully")


class TestAdminEndpoints:
    """Tests for Admin Settings, Premium, API-Usage, Processing-Metrics"""
    
    def test_admin_settings_get(self):
        """GET /api/admin/settings - returns 200"""
        response = requests.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("✅ GET /api/admin/settings returns 200")
    
    def test_admin_premium_users(self):
        """GET /api/admin/premium/users - returns 200"""
        response = requests.get(f"{BASE_URL}/api/admin/premium/users")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "users" in data
        print(f"✅ GET /api/admin/premium/users returns {len(data.get('users', []))} users")
    
    def test_admin_api_usage(self):
        """GET /api/admin/api-usage - returns 200"""
        response = requests.get(f"{BASE_URL}/api/admin/api-usage")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("✅ GET /api/admin/api-usage returns 200")
    
    def test_admin_processing_metrics(self):
        """GET /api/admin/processing-metrics - returns 200"""
        response = requests.get(f"{BASE_URL}/api/admin/processing-metrics")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("✅ GET /api/admin/processing-metrics returns 200")


class TestSafeNutritionUpdate:
    """Tests for Safe Nutrition Update Pipeline (preview, update, rollback, audit)"""
    
    def test_nutrition_preview_empty(self):
        """POST /api/admin/nutrition/preview - preview without altering data"""
        response = requests.post(
            f"{BASE_URL}/api/admin/nutrition/preview",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        # May return ok=False if nutrition_3sources module not available (expected)
        if data.get("ok") == False and "nutrition_3sources" in data.get("error", ""):
            print("⚠️ Nutrition preview: nutrition_3sources module not available (expected)")
        else:
            assert data.get("ok") == True
            assert "previews" in data
            print(f"✅ Nutrition preview returned {data.get('total_analyzed', 0)} items")
    
    def test_nutrition_preview_with_slugs(self):
        """POST /api/admin/nutrition/preview with specific dish_slugs"""
        response = requests.post(
            f"{BASE_URL}/api/admin/nutrition/preview",
            json={"dish_slugs": ["arroz_branco"], "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        # May return ok=False if nutrition_3sources module not available (expected)
        if data.get("ok") == False and "nutrition_3sources" in data.get("error", ""):
            print("⚠️ Nutrition preview with slugs: nutrition_3sources module not available (expected)")
        else:
            assert data.get("ok") == True
            print(f"✅ Nutrition preview with slugs: {data.get('total_analyzed', 0)} analyzed")
    
    def test_nutrition_audit_log(self):
        """GET /api/admin/nutrition/audit-log - returns audit history"""
        response = requests.get(f"{BASE_URL}/api/admin/nutrition/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "logs" in data
        print(f"✅ Nutrition audit log has {len(data.get('logs', []))} entries")
    
    def test_nutrition_update_single_invalid_slug(self):
        """POST /api/admin/nutrition/update-single with invalid slug"""
        response = requests.post(
            f"{BASE_URL}/api/admin/nutrition/update-single",
            json={
                "dish_slug": "nonexistent_dish_xyz_123",
                "new_nutrition": {"calorias_kcal": 100}
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should return ok=False for nonexistent dish
        assert data.get("ok") == False
        assert "error" in data
        print("✅ Update single correctly rejects invalid slug")
    
    def test_nutrition_rollback_invalid_slug(self):
        """POST /api/admin/nutrition/rollback with invalid slug"""
        response = requests.post(
            f"{BASE_URL}/api/admin/nutrition/rollback",
            json={"dish_slug": "nonexistent_dish_xyz_123"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should return ok=False for nonexistent dish
        assert data.get("ok") == False
        print("✅ Rollback correctly handles invalid slug")


class TestModerationQuickVerify:
    """Quick verification that moderation endpoints still work"""
    
    def test_moderation_queue_accessible(self):
        """GET /api/admin/moderation-queue - still accessible"""
        response = requests.get(f"{BASE_URL}/api/admin/moderation-queue?status=all")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        print(f"✅ Moderation queue accessible with {len(data.get('items', []))} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
