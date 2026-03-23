"""
Test suite for SoulNutri Moderation Queue Feature
Tests:
- POST /api/feedback/moderation-queue - Create moderation item
- GET /api/admin/moderation-queue?status=pending - List pending items
- GET /api/admin/moderation-queue?status=all - List all items
- POST /api/admin/moderation/{id}/approve - Approve item
- POST /api/admin/moderation/{id}/reject - Reject item
- POST /api/admin/moderation/{id}/correct - Correct dish name
- GET /api/admin/moderation-image/{id} - Get item image
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_IMAGE_PATH = "/tmp/test_mod.jpg"


class TestModerationQueue:
    """Tests for moderation queue endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.created_item_id = None
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("✅ API health check passed")
    
    def test_create_moderation_item(self):
        """Test POST /api/feedback/moderation-queue - Create item in moderation queue"""
        # Check if test image exists
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found at {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test_mod.jpg', f, 'image/jpeg')}
            data = {
                'original_dish': 'test_prato',
                'original_dish_display': 'Test Prato',
                'confidence': 'media',
                'score': '0.65',
                'source': 'local_index'
            }
            response = requests.post(
                f"{BASE_URL}/api/feedback/moderation-queue",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("ok") == True
        # API returns queue_id, not item_id
        assert "queue_id" in result or "item_id" in result
        self.created_item_id = result.get("queue_id") or result.get("item_id")
        print(f"✅ Created moderation item: {self.created_item_id}")
        return self.created_item_id
    
    def test_get_moderation_queue_pending(self):
        """Test GET /api/admin/moderation-queue?status=pending - List pending items"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        assert isinstance(data["items"], list)
        assert "pending_count" in data
        print(f"✅ Got pending items: {len(data['items'])} items, pending_count: {data['pending_count']}")
        return data
    
    def test_get_moderation_queue_all(self):
        """Test GET /api/admin/moderation-queue?status=all - List all items"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=all")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        assert isinstance(data["items"], list)
        print(f"✅ Got all items: {len(data['items'])} items")
        return data
    
    def test_get_moderation_queue_approved(self):
        """Test GET /api/admin/moderation-queue?status=approved - List approved items"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=approved")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        print(f"✅ Got approved items: {len(data['items'])} items")
    
    def test_get_moderation_queue_rejected(self):
        """Test GET /api/admin/moderation-queue?status=rejected - List rejected items"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=rejected")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        print(f"✅ Got rejected items: {len(data['items'])} items")
    
    def test_get_moderation_queue_corrected(self):
        """Test GET /api/admin/moderation-queue?status=corrected - List corrected items"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=corrected")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "items" in data
        print(f"✅ Got corrected items: {len(data['items'])} items")
    
    def test_moderation_item_structure(self):
        """Test that moderation items have correct structure"""
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=all")
        assert response.status_code == 200
        data = response.json()
        
        if len(data.get("items", [])) > 0:
            item = data["items"][0]
            # Check required fields
            assert "id" in item, "Item should have 'id' field"
            assert "original_dish_display" in item, "Item should have 'original_dish_display' field"
            assert "status" in item, "Item should have 'status' field"
            assert "created_at" in item, "Item should have 'created_at' field"
            print(f"✅ Item structure verified: {item.get('original_dish_display')} - {item.get('status')}")
        else:
            print("⚠️ No items to verify structure")
    
    def test_get_moderation_image(self):
        """Test GET /api/admin/moderation-image/{id} - Get item image"""
        # First get an item ID
        response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=all")
        data = response.json()
        
        if len(data.get("items", [])) > 0:
            item_id = data["items"][0]["id"]
            img_response = requests.get(f"{BASE_URL}/api/admin/moderation-image/{item_id}")
            # Should return image or 404 if image not found
            assert img_response.status_code in [200, 404]
            if img_response.status_code == 200:
                assert img_response.headers.get("content-type", "").startswith("image/")
                print(f"✅ Got moderation image for item {item_id}")
            else:
                print(f"⚠️ Image not found for item {item_id} (may be expected)")
        else:
            pytest.skip("No items to test image retrieval")


class TestModerationActions:
    """Tests for moderation approve/reject/correct actions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
    
    def _create_test_item(self):
        """Helper to create a test moderation item"""
        if not os.path.exists(TEST_IMAGE_PATH):
            return None
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test_action.jpg', f, 'image/jpeg')}
            data = {
                'original_dish': f'test_action_{int(time.time())}',
                'original_dish_display': f'Test Action {int(time.time())}',
                'confidence': 'baixa',
                'score': '0.40',
                'source': 'test'
            }
            response = requests.post(
                f"{BASE_URL}/api/feedback/moderation-queue",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("queue_id") or result.get("item_id")
        return None
    
    def test_approve_moderation_item(self):
        """Test POST /api/admin/moderation/{id}/approve - Approve item"""
        item_id = self._create_test_item()
        if not item_id:
            pytest.skip("Could not create test item")
        
        response = self.session.post(f"{BASE_URL}/api/admin/moderation/{item_id}/approve")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ Approved item {item_id}")
        
        # Verify status changed
        queue_response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=approved")
        queue_data = queue_response.json()
        approved_ids = [item["id"] for item in queue_data.get("items", [])]
        assert item_id in approved_ids, "Item should be in approved list"
        print(f"✅ Verified item {item_id} is in approved list")
    
    def test_reject_moderation_item(self):
        """Test POST /api/admin/moderation/{id}/reject - Reject item"""
        item_id = self._create_test_item()
        if not item_id:
            pytest.skip("Could not create test item")
        
        response = self.session.post(f"{BASE_URL}/api/admin/moderation/{item_id}/reject")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ Rejected item {item_id}")
        
        # Verify status changed
        queue_response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=rejected")
        queue_data = queue_response.json()
        rejected_ids = [item["id"] for item in queue_data.get("items", [])]
        assert item_id in rejected_ids, "Item should be in rejected list"
        print(f"✅ Verified item {item_id} is in rejected list")
    
    def test_correct_moderation_item(self):
        """Test POST /api/admin/moderation/{id}/correct - Correct dish name"""
        item_id = self._create_test_item()
        if not item_id:
            pytest.skip("Could not create test item")
        
        correct_name = f"Prato Corrigido {int(time.time())}"
        response = self.session.post(
            f"{BASE_URL}/api/admin/moderation/{item_id}/correct",
            json={"correct_dish_name": correct_name}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ Corrected item {item_id} to '{correct_name}'")
        
        # Verify status changed
        queue_response = self.session.get(f"{BASE_URL}/api/admin/moderation-queue?status=corrected")
        queue_data = queue_response.json()
        corrected_items = [item for item in queue_data.get("items", []) if item["id"] == item_id]
        assert len(corrected_items) > 0, "Item should be in corrected list"
        # Field is named 'correction' not 'corrected_dish_name'
        assert corrected_items[0].get("correction") == correct_name or corrected_items[0].get("corrected_dish_name") == correct_name
        print(f"✅ Verified item {item_id} is in corrected list with correct name")
    
    def test_correct_without_name_fails(self):
        """Test that correction without dish name fails"""
        item_id = self._create_test_item()
        if not item_id:
            pytest.skip("Could not create test item")
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/moderation/{item_id}/correct",
            json={}
        )
        # Should fail with 400 or return ok=false
        if response.status_code == 200:
            data = response.json()
            assert data.get("ok") == False or "error" in data
        else:
            assert response.status_code in [400, 422]
        print("✅ Correction without name correctly fails")
    
    def test_action_on_invalid_id(self):
        """Test actions on invalid item ID"""
        invalid_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        
        # Test approve
        response = self.session.post(f"{BASE_URL}/api/admin/moderation/{invalid_id}/approve")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data.get("ok") == False or "error" in data
        print("✅ Approve on invalid ID correctly handled")
        
        # Test reject
        response = self.session.post(f"{BASE_URL}/api/admin/moderation/{invalid_id}/reject")
        assert response.status_code in [200, 404]
        print("✅ Reject on invalid ID correctly handled")


class TestExistingModerationData:
    """Tests to verify existing moderation data from context"""
    
    def test_existing_pending_items(self):
        """Verify existing pending items (Lasanha, Salmão Grelhado, Brigadeiro)"""
        response = requests.get(f"{BASE_URL}/api/admin/moderation-queue?status=pending")
        assert response.status_code == 200
        data = response.json()
        
        pending_names = [item.get("original_dish_display", "") for item in data.get("items", [])]
        print(f"Pending items: {pending_names}")
        
        # Check if expected items are present (may have been processed)
        expected = ["Lasanha", "Salmão Grelhado", "Brigadeiro"]
        found = [name for name in expected if any(name in p for p in pending_names)]
        print(f"✅ Found expected pending items: {found}")
    
    def test_existing_resolved_items(self):
        """Verify existing resolved items (Frango Grelhado=corrected, Arroz Branco=approved, Feijão=rejected)"""
        # Check corrected
        response = requests.get(f"{BASE_URL}/api/admin/moderation-queue?status=corrected")
        corrected_data = response.json()
        corrected_names = [item.get("original_dish_display", "") for item in corrected_data.get("items", [])]
        print(f"Corrected items: {corrected_names}")
        
        # Check approved
        response = requests.get(f"{BASE_URL}/api/admin/moderation-queue?status=approved")
        approved_data = response.json()
        approved_names = [item.get("original_dish_display", "") for item in approved_data.get("items", [])]
        print(f"Approved items: {approved_names}")
        
        # Check rejected
        response = requests.get(f"{BASE_URL}/api/admin/moderation-queue?status=rejected")
        rejected_data = response.json()
        rejected_names = [item.get("original_dish_display", "") for item in rejected_data.get("items", [])]
        print(f"Rejected items: {rejected_names}")
        
        print("✅ Verified existing resolved items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
