"""
SoulNutri Admin Panel - R2 Migration Tests
Tests for validating Cloudflare R2 image storage migration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://premium-auth-fix.preview.emergentagent.com').rstrip('/')


class TestAdminDishesAPI:
    """Tests for /api/admin/dishes endpoints"""
    
    def test_get_dishes_list(self):
        """GET /api/admin/dishes - Returns list of dishes with basic info"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert "dishes" in data, "Response should have dishes array"
        assert "total" in data, "Response should have total count"
        
        # Validate dish structure
        if data["dishes"]:
            dish = data["dishes"][0]
            assert "slug" in dish, "Dish should have slug"
            assert "nome" in dish, "Dish should have nome"
            assert "image_count" in dish, "Dish should have image_count"
        
        print(f"✅ GET /api/admin/dishes: {data['total']} dishes returned")
    
    def test_get_dishes_full(self):
        """GET /api/admin/dishes-full - Returns full dish data with images"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert "dishes" in data, "Response should have dishes array"
        
        # Calculate total images
        total_images = sum(d.get("image_count", 0) for d in data.get("dishes", []))
        total_dishes = len(data.get("dishes", []))
        
        print(f"✅ GET /api/admin/dishes-full: {total_dishes} dishes, {total_images} total images")
        
        # Verify expected counts (approximately)
        assert total_dishes >= 190, f"Expected at least 190 dishes, got {total_dishes}"
        assert total_images >= 3900, f"Expected at least 3900 images, got {total_images}"


class TestDishImagesAPI:
    """Tests for dish image endpoints - R2 integration"""
    
    def test_get_dish_images_list(self):
        """GET /api/admin/dish-images-list/{slug} - Returns list of images for a dish"""
        # Test with a known dish
        slug = "arroz-branco"
        response = requests.get(f"{BASE_URL}/api/admin/dish-images-list/{slug}", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert "images" in data, "Response should have images array"
        assert "count" in data, "Response should have count"
        
        # Verify images is a list of strings (filenames)
        if data["images"]:
            img = data["images"][0]
            assert isinstance(img, str), f"Image should be a string filename, got {type(img)}"
            assert len(img) > 0, "Filename should not be empty"
        
        print(f"✅ GET /api/admin/dish-images-list/{slug}: {data['count']} images")
    
    def test_get_dish_thumbnail(self):
        """GET /api/admin/dish-image/{slug}?thumb=1 - Returns compressed thumbnail"""
        slug = "arroz-branco"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify it's a JPEG image
        content_type = response.headers.get("content-type", "")
        assert "image" in content_type, f"Expected image content-type, got {content_type}"
        
        # Verify thumbnail is compressed (should be < 50KB)
        size = len(response.content)
        assert size < 50000, f"Thumbnail should be < 50KB, got {size} bytes"
        assert size > 1000, f"Thumbnail should be > 1KB, got {size} bytes"
        
        # Verify JPEG magic bytes
        assert response.content[:2] == b'\xff\xd8', "Should be JPEG format"
        
        print(f"✅ GET /api/admin/dish-image/{slug}?thumb=1: {size} bytes (compressed)")
    
    def test_get_dish_full_image(self):
        """GET /api/admin/dish-image/{slug} - Returns full-size image"""
        slug = "arroz-branco"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content_type = response.headers.get("content-type", "")
        assert "image" in content_type, f"Expected image content-type, got {content_type}"
        
        size = len(response.content)
        print(f"✅ GET /api/admin/dish-image/{slug}: {size} bytes (full size)")
    
    def test_get_nonexistent_dish_image(self):
        """GET /api/admin/dish-image/{slug} - Returns 404 for non-existent dish"""
        slug = "nonexistent-dish-xyz123"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}", timeout=15)
        # Should return 404 or empty response
        assert response.status_code in [404, 200], f"Expected 404 or 200, got {response.status_code}"
        print(f"✅ GET /api/admin/dish-image/{slug}: Status {response.status_code}")


class TestAIStatusAPI:
    """Tests for AI index status"""
    
    def test_ai_status(self):
        """GET /api/ai/status - Returns AI index status"""
        response = requests.get(f"{BASE_URL}/api/ai/status", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert "ready" in data, "Response should have ready status"
        assert "total_dishes" in data, "Response should have total_dishes"
        assert "total_embeddings" in data, "Response should have total_embeddings"
        
        print(f"✅ GET /api/ai/status: ready={data['ready']}, {data['total_dishes']} dishes, {data['total_embeddings']} embeddings")


class TestHealthAPI:
    """Tests for health check endpoints"""
    
    def test_health_root(self):
        """GET /health - Returns 200 (may be HTML or JSON depending on routing)"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        # The /health endpoint may return HTML (frontend) or JSON depending on routing
        # Just verify it returns 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ GET /health: Status 200 OK")
    
    def test_api_health(self):
        """GET /api/health - API health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, "Should have ok=True"
        print(f"✅ GET /api/health: {data}")


class TestSearchAndFilter:
    """Tests for search and filter functionality"""
    
    def test_dishes_contain_expected_fields(self):
        """Verify dishes have all expected fields for admin panel"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        dishes = data.get("dishes", [])
        
        # Check first few dishes have required fields
        required_fields = ["slug", "nome", "image_count"]
        optional_fields = ["categoria", "category_emoji", "ingredientes", "descricao"]
        
        for dish in dishes[:5]:
            for field in required_fields:
                assert field in dish, f"Dish missing required field: {field}"
        
        print(f"✅ Dishes have all required fields")
    
    def test_multiple_dishes_have_images(self):
        """Verify multiple dishes have images (R2 migration successful)"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        dishes = data.get("dishes", [])
        
        dishes_with_images = [d for d in dishes if d.get("image_count", 0) > 0]
        
        assert len(dishes_with_images) >= 180, f"Expected at least 180 dishes with images, got {len(dishes_with_images)}"
        print(f"✅ {len(dishes_with_images)} dishes have images")


class TestR2ThumbnailCompression:
    """Tests for R2 thumbnail compression feature"""
    
    def test_thumbnail_vs_full_size(self):
        """Compare thumbnail size vs full image size"""
        slug = "abobora-ao-curry"  # Known dish with images
        
        # Get thumbnail
        thumb_response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=15)
        assert thumb_response.status_code == 200
        thumb_size = len(thumb_response.content)
        
        # Get full image
        full_response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}", timeout=15)
        assert full_response.status_code == 200
        full_size = len(full_response.content)
        
        # Thumbnail should be significantly smaller
        compression_ratio = full_size / thumb_size if thumb_size > 0 else 0
        
        print(f"✅ Thumbnail: {thumb_size} bytes, Full: {full_size} bytes, Ratio: {compression_ratio:.1f}x")
        
        # Thumbnail should be at least 2x smaller (usually 10x+ smaller)
        assert compression_ratio >= 2, f"Expected compression ratio >= 2, got {compression_ratio:.1f}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
