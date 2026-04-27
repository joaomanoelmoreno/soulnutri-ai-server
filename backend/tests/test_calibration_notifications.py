# -*- coding: utf-8 -*-
"""
Test Suite: Calibration Clear-All + Notifications + References
Tests for:
1. DELETE /api/ai/calibration/clear-all - zera todas as amostras
2. GET /api/ai/calibration - retorna stats com total_samples=0 após clear
3. POST /api/ai/calibration/log - registra nova amostra
4. DELETE /api/ai/calibration/{sample_id} - deleta amostra individual
5. POST /api/notifications/generate - gera notificação com referências
6. GET /api/notifications/{user_pin} - retorna notificações com unread count
7. POST /api/notifications/{user_pin}/read - marca como lida
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://soulnutri-audit.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_PIN = "1234"
TEST_NAME = "Teste SoulNutri"


class TestCalibrationClearAll:
    """Tests for calibration clear-all endpoint"""
    
    def test_clear_all_calibration_endpoint_exists(self):
        """DELETE /api/ai/calibration/clear-all should exist and respond"""
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "ok" in data, "Response should have 'ok' field"
        print(f"✓ Clear-all endpoint responded: ok={data.get('ok')}, deleted_count={data.get('deleted_count')}")
    
    def test_clear_all_returns_deleted_count(self):
        """DELETE /api/ai/calibration/clear-all should return deleted_count"""
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert "deleted_count" in data, "Response should have 'deleted_count' field"
        print(f"✓ Clear-all returned deleted_count: {data.get('deleted_count')}")
    
    def test_calibration_stats_after_clear(self):
        """GET /api/ai/calibration should return total_samples=0 after clear"""
        # First clear all
        clear_response = requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all", timeout=10)
        assert clear_response.status_code == 200
        
        # Then check stats
        response = requests.get(f"{BASE_URL}/api/ai/calibration", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        
        stats = data.get("stats", {})
        assert stats.get("total_samples") == 0, f"Expected total_samples=0 after clear, got {stats.get('total_samples')}"
        print(f"✓ After clear-all, total_samples=0 confirmed")


class TestCalibrationLog:
    """Tests for calibration log endpoint"""
    
    def test_log_calibration_sample_correct(self):
        """POST /api/ai/calibration/log should register correct sample"""
        form_data = {
            "dish_clip": "frango_grelhado",
            "dish_real": "frango_grelhado",
            "is_correct": "true",
            "score": "0.92",
            "confidence": "alta",
            "source": "local_index"
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=form_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        # API returns 'id' field
        assert "id" in data or "sample_id" in data, f"Response should have 'id' or 'sample_id', got {data}"
        sample_id = data.get("id") or data.get("sample_id")
        print(f"✓ Logged correct sample, id={sample_id}")
        return sample_id
    
    def test_log_calibration_sample_incorrect(self):
        """POST /api/ai/calibration/log should register incorrect sample"""
        form_data = {
            "dish_clip": "arroz_branco",
            "dish_real": "arroz_integral",
            "is_correct": "false",
            "score": "0.65",
            "confidence": "media",
            "source": "local_index"
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=form_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        sample_id = data.get("id") or data.get("sample_id")
        print(f"✓ Logged incorrect sample, id={sample_id}")
        return sample_id


class TestCalibrationDelete:
    """Tests for calibration delete individual sample"""
    
    def test_delete_calibration_sample(self):
        """DELETE /api/ai/calibration/{sample_id} should delete sample"""
        # First create a sample
        form_data = {
            "dish_clip": "test_delete",
            "dish_real": "test_delete",
            "is_correct": "true",
            "score": "0.88",
            "confidence": "alta",
            "source": "test"
        }
        create_response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=form_data, timeout=10)
        assert create_response.status_code == 200
        create_data = create_response.json()
        sample_id = create_data.get("id") or create_data.get("sample_id")
        assert sample_id, f"Should get id from create, got {create_data}"
        
        # Now delete it
        delete_response = requests.delete(f"{BASE_URL}/api/ai/calibration/{sample_id}", timeout=10)
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        print(f"✓ Deleted sample {sample_id}")
    
    def test_delete_nonexistent_sample(self):
        """DELETE /api/ai/calibration/{sample_id} should return ok=false for invalid ID"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/{fake_id}", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == False, f"Expected ok=False for non-existent sample, got {data}"
        print(f"✓ Non-existent sample returns ok=False")


class TestNotificationsGenerate:
    """Tests for notification generation endpoint"""
    
    def test_generate_notification_endpoint(self):
        """POST /api/notifications/generate should generate notification"""
        payload = {
            "user_pin": TEST_PIN,
            "user_name": TEST_NAME
        }
        response = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Either ok=True (new notification) or ok=False with reason=already_sent_today
        assert "ok" in data, "Response should have 'ok' field"
        
        if data.get("ok"):
            notification = data.get("notification", {})
            assert "title" in notification, "Notification should have 'title'"
            assert "message" in notification, "Notification should have 'message'"
            assert "references" in notification, "Notification should have 'references'"
            print(f"✓ Generated notification: {notification.get('title')}")
            print(f"  References: {len(notification.get('references', []))} links")
        else:
            reason = data.get("reason", "")
            print(f"✓ Notification not generated: {reason}")
    
    def test_notification_has_references(self):
        """Generated notification should include references with URLs"""
        # First clear any existing notification for today by using a unique pin
        unique_pin = f"test_{int(time.time())}"
        payload = {
            "user_pin": unique_pin,
            "user_name": "Test User"
        }
        response = requests.post(
            f"{BASE_URL}/api/notifications/generate",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("ok"):
            notification = data.get("notification", {})
            references = notification.get("references", [])
            assert len(references) > 0, "Notification should have at least one reference"
            
            for ref in references:
                assert "source" in ref, "Reference should have 'source'"
                assert "url" in ref, "Reference should have 'url'"
                assert ref["url"].startswith("http"), f"URL should be valid: {ref['url']}"
            
            print(f"✓ Notification has {len(references)} valid references")
            for ref in references:
                print(f"  - {ref.get('source')}: {ref.get('url')[:50]}...")


class TestNotificationsGet:
    """Tests for getting user notifications"""
    
    def test_get_notifications_endpoint(self):
        """GET /api/notifications/{user_pin} should return notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications/{TEST_PIN}", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert "notifications" in data, "Response should have 'notifications'"
        assert "unread" in data, "Response should have 'unread' count"
        
        notifications = data.get("notifications", [])
        unread = data.get("unread", 0)
        print(f"✓ Got {len(notifications)} notifications, {unread} unread")
        
        # Check notification structure if any exist
        if notifications:
            n = notifications[0]
            assert "title" in n, "Notification should have 'title'"
            assert "message" in n, "Notification should have 'message'"
            print(f"  Latest: {n.get('title')}")


class TestNotificationsRead:
    """Tests for marking notifications as read"""
    
    def test_mark_notification_read(self):
        """POST /api/notifications/{user_pin}/read should mark as read"""
        # First get notifications to find a date
        get_response = requests.get(f"{BASE_URL}/api/notifications/{TEST_PIN}", timeout=10)
        assert get_response.status_code == 200
        data = get_response.json()
        
        notifications = data.get("notifications", [])
        if not notifications:
            print("⚠ No notifications to mark as read, skipping test")
            return
        
        # Get the date of the first notification
        notification_date = notifications[0].get("date")
        if not notification_date:
            print("⚠ Notification has no date, skipping test")
            return
        
        # Mark as read
        payload = {"date": notification_date}
        response = requests.post(
            f"{BASE_URL}/api/notifications/{TEST_PIN}/read",
            json=payload,
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        print(f"✓ Marked notification from {notification_date} as read")


class TestCalibrationFullFlow:
    """Integration test for full calibration flow"""
    
    def test_full_calibration_flow(self):
        """Test: clear-all -> log samples -> verify stats -> delete sample"""
        # 1. Clear all
        clear_response = requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all", timeout=10)
        assert clear_response.status_code == 200
        print("Step 1: Cleared all calibration samples")
        
        # 2. Verify empty
        stats_response = requests.get(f"{BASE_URL}/api/ai/calibration", timeout=10)
        assert stats_response.status_code == 200
        stats = stats_response.json().get("stats", {})
        assert stats.get("total_samples") == 0
        print("Step 2: Verified total_samples=0")
        
        # 3. Log a correct sample
        form_data = {
            "dish_clip": "salada_verde",
            "dish_real": "salada_verde",
            "is_correct": "true",
            "score": "0.95",
            "confidence": "alta",
            "source": "local_index"
        }
        log_response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=form_data, timeout=10)
        assert log_response.status_code == 200
        log_data = log_response.json()
        sample_id = log_data.get("id") or log_data.get("sample_id")
        assert sample_id, f"Should get id from log, got {log_data}"
        print(f"Step 3: Logged sample {sample_id}")
        
        # 4. Verify stats updated
        stats_response = requests.get(f"{BASE_URL}/api/ai/calibration", timeout=10)
        assert stats_response.status_code == 200
        stats = stats_response.json().get("stats", {})
        assert stats.get("total_samples") >= 1, f"Expected at least 1 sample, got {stats.get('total_samples')}"
        print(f"Step 4: Verified total_samples={stats.get('total_samples')}")
        
        # 5. Delete the sample
        delete_response = requests.delete(f"{BASE_URL}/api/ai/calibration/{sample_id}", timeout=10)
        assert delete_response.status_code == 200
        assert delete_response.json().get("ok") == True
        print(f"Step 5: Deleted sample {sample_id}")
        
        print("✓ Full calibration flow completed successfully")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
