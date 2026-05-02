"""
SoulNutri - Iteration 11 Tests
Tests for:
1. Admin Upload Fotos - dish names in Title Case
2. Admin Calibration - Zerar Tudo button
3. Premium layout features
4. Notifications API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://soulnutri-ai-fix.preview.emergentagent.com').rstrip('/')


class TestUploadFotosAPI:
    """Tests for Upload Fotos tab - dish names display"""
    
    def test_upload_status_returns_dishes(self):
        """GET /api/upload/status should return dishes with names"""
        response = requests.get(f"{BASE_URL}/api/upload/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'dishes' in data
        assert 'total_dishes' in data
        print(f"Total dishes: {data['total_dishes']}")
    
    def test_dish_names_are_title_case(self):
        """Dish names should be in Title Case, not slugs with hyphens"""
        response = requests.get(f"{BASE_URL}/api/upload/status")
        assert response.status_code == 200
        data = response.json()
        
        dishes = data.get('dishes', {})
        assert len(dishes) > 0, "No dishes found"
        
        # Check first 20 dish names
        dish_names = list(dishes.keys())[:20]
        
        for name in dish_names:
            # Should NOT have hyphens (slug format)
            assert '-' not in name, f"Dish name '{name}' contains hyphens (slug format)"
            # Should have spaces or be single word
            # Title case check: first letter of each word should be uppercase
            words = name.split()
            for word in words:
                if word and word[0].isalpha():
                    # Allow lowercase for Portuguese prepositions and articles
                    if word.lower() not in ['ao', 'a', 'com', 'de', 'da', 'do', 'e', 'ou', 's/', 'c/', 'em', 'no', 'na', 'os', 'as']:
                        assert word[0].isupper(), f"Word '{word}' in '{name}' is not Title Case"
        
        print(f"Verified {len(dish_names)} dish names are in Title Case")
    
    def test_total_dishes_count(self):
        """Should have 196 dishes (after merge of duplicates)"""
        response = requests.get(f"{BASE_URL}/api/upload/status")
        assert response.status_code == 200
        data = response.json()
        
        total = data.get('total_dishes', 0)
        assert total == 196, f"Expected 196 dishes, got {total}"
        print(f"Total dishes: {total}")


class TestCalibrationAPI:
    """Tests for Calibration CLIP tab"""
    
    def test_calibration_clear_all_endpoint_exists(self):
        """DELETE /api/ai/calibration/clear-all should exist and work"""
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'deleted_count' in data
        print(f"Deleted {data['deleted_count']} samples")
    
    def test_calibration_stats_after_clear(self):
        """GET /api/ai/calibration should return 0 samples after clear"""
        # First clear all
        requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all")
        
        # Then check stats
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert data.get('stats', {}).get('total_samples') == 0
        print("Calibration stats: 0 samples after clear")
    
    def test_calibration_log_sample(self):
        """POST /api/ai/calibration/log should register a sample"""
        form_data = {
            'dish_clip': 'arroz-branco',
            'dish_real': 'arroz-branco',
            'is_correct': 'true',
            'score': '0.95',
            'confidence': 'alta',
            'source': 'test'
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'id' in data
        print(f"Logged sample with id: {data['id']}")
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/ai/calibration/clear-all")


class TestNotificationsAPI:
    """Tests for Notifications API"""
    
    def test_get_notifications_for_premium_user(self):
        """GET /api/notifications/{pin} should return notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications/1234")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'notifications' in data
        assert 'unread' in data
        print(f"Found {len(data['notifications'])} notifications, {data['unread']} unread")
    
    def test_notifications_have_references(self):
        """Notifications should have references array"""
        response = requests.get(f"{BASE_URL}/api/notifications/1234")
        assert response.status_code == 200
        data = response.json()
        
        notifications = data.get('notifications', [])
        if notifications:
            notif = notifications[0]
            # References may or may not be present
            if 'references' in notif:
                refs = notif['references']
                assert isinstance(refs, list)
                if refs:
                    ref = refs[0]
                    assert 'source' in ref
                    assert 'url' in ref
                    print(f"Notification has {len(refs)} references")
            else:
                print("Notification has no references (optional)")
        else:
            print("No notifications found (user may not have any)")


class TestPremiumLogin:
    """Tests for Premium user login"""
    
    def test_premium_login_with_valid_credentials(self):
        """POST /api/premium/login should work with valid PIN and name"""
        form_data = {
            'pin': '1234',
            'nome': 'Teste SoulNutri'
        }
        response = requests.post(f"{BASE_URL}/api/premium/login", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'user' in data
        print(f"Premium login successful for: {data['user'].get('nome')}")
    
    def test_premium_login_with_invalid_credentials(self):
        """POST /api/premium/login should fail with invalid credentials"""
        form_data = {
            'pin': '9999',
            'nome': 'Invalid User'
        }
        response = requests.post(f"{BASE_URL}/api/premium/login", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == False
        print("Premium login correctly rejected invalid credentials")


class TestAIStatus:
    """Tests for AI status endpoint"""
    
    def test_ai_status(self):
        """GET /api/ai/status should return index status"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'ready' in data
        assert 'total_dishes' in data
        print(f"AI Index: {data['total_dishes']} dishes, ready={data['ready']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
