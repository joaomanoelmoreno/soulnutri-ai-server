"""
Test Admin Panel Features for SoulNutri
- Thumbnail endpoint (thumb=1 parameter)
- Move image functionality with dropdown validation
- Delete image with two-click confirmation
- Dishes-full endpoint with ingredientes field
- PUT dish update endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminDishesEndpoint:
    """Test GET /api/admin/dishes-full endpoint"""
    
    def test_dishes_full_returns_206_dishes(self):
        """Verify dishes-full returns all 206 dishes"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert len(data.get("dishes", [])) == 206
        print(f"✓ dishes-full returns {len(data['dishes'])} dishes")
    
    def test_dishes_have_ingredientes_field(self):
        """Verify most dishes have ingredientes field populated"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        data = response.json()
        dishes = data.get("dishes", [])
        
        with_ingredients = [d for d in dishes if d.get("ingredientes") and len(d.get("ingredientes", [])) > 0]
        without_ingredients = [d for d in dishes if not d.get("ingredientes") or len(d.get("ingredientes", [])) == 0]
        
        # Per context: 14 out of 206 have no ingredients - this is expected
        assert len(with_ingredients) >= 190, f"Expected at least 190 dishes with ingredients, got {len(with_ingredients)}"
        print(f"✓ {len(with_ingredients)} dishes have ingredientes, {len(without_ingredients)} without (expected ~14)")
    
    def test_dish_structure_complete(self):
        """Verify dish structure has required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        data = response.json()
        dish = data.get("dishes", [])[0]
        
        required_fields = ["slug", "nome", "image_count", "first_image"]
        for field in required_fields:
            assert field in dish, f"Missing field: {field}"
        print(f"✓ Dish structure has all required fields: {required_fields}")


class TestThumbnailEndpoint:
    """Test GET /api/admin/dish-image/{slug}?thumb=1 endpoint"""
    
    def test_thumbnail_returns_compressed_image(self):
        """Verify thumb=1 returns smaller image than full size"""
        slug = "arroz-branco"
        
        # Get thumbnail
        thumb_response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=30)
        assert thumb_response.status_code == 200
        thumb_size = len(thumb_response.content)
        
        # Get full image
        full_response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}", timeout=30)
        assert full_response.status_code == 200
        full_size = len(full_response.content)
        
        # Thumbnail should be significantly smaller (at least 50% smaller)
        assert thumb_size < full_size * 0.5, f"Thumbnail ({thumb_size}) should be much smaller than full ({full_size})"
        print(f"✓ Thumbnail: {thumb_size/1024:.1f}KB vs Full: {full_size/1024:.1f}KB (compression ratio: {thumb_size/full_size:.2%})")
    
    def test_thumbnail_is_valid_jpeg(self):
        """Verify thumbnail returns valid JPEG"""
        slug = "arroz-branco"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=30)
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/jpeg"
        # JPEG magic bytes
        assert response.content[:2] == b'\xff\xd8'
        print(f"✓ Thumbnail is valid JPEG ({len(response.content)/1024:.1f}KB)")
    
    def test_specific_image_with_thumbnail(self):
        """Verify specific image query with thumb=1 works"""
        slug = "arroz-branco"
        img = "arrozbranco026.jpeg"
        
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?img={img}&thumb=1", timeout=30)
        assert response.status_code == 200
        assert len(response.content) < 50000  # Should be under 50KB for thumbnail
        print(f"✓ Specific image thumbnail: {len(response.content)/1024:.1f}KB")


class TestMoveImageEndpoint:
    """Test POST /api/admin/move-image endpoint"""
    
    def test_move_image_validates_target_exists(self):
        """Verify move-image returns error for non-existent target dish"""
        payload = {
            "source_dish": "arroz-branco",
            "target_dish": "prato-que-nao-existe-xyz",
            "image_name": "test.jpg"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/move-image", json=payload, timeout=30)
        assert response.status_code == 404
        data = response.json()
        assert data.get("ok") == False
        assert "nao encontrado" in data.get("error", "").lower()
        print(f"✓ Move image validates target exists: {data.get('error')}")
    
    def test_move_image_requires_all_fields(self):
        """Verify move-image requires source_dish, target_dish, image_name"""
        # Missing target_dish
        payload = {
            "source_dish": "arroz-branco",
            "image_name": "test.jpg"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/move-image", json=payload, timeout=30)
        assert response.status_code == 400
        data = response.json()
        assert data.get("ok") == False
        print(f"✓ Move image requires all fields: {data.get('error')}")
    
    def test_move_image_validates_source_image_exists(self):
        """Verify move-image returns error for non-existent source image"""
        payload = {
            "source_dish": "arroz-branco",
            "target_dish": "arroz-7-graos",  # Valid target
            "image_name": "imagem-que-nao-existe-xyz.jpg"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/move-image", json=payload, timeout=30)
        assert response.status_code == 404
        data = response.json()
        assert data.get("ok") == False
        assert "nao encontrada" in data.get("error", "").lower()
        print(f"✓ Move image validates source image exists: {data.get('error')}")


class TestDishImagesListEndpoint:
    """Test GET /api/admin/dish-images-list/{slug} endpoint"""
    
    def test_dish_images_list_returns_images(self):
        """Verify dish-images-list returns list of image filenames"""
        slug = "arroz-branco"
        response = requests.get(f"{BASE_URL}/api/admin/dish-images-list/{slug}", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "images" in data
        assert "count" in data
        assert data["count"] > 0
        assert len(data["images"]) == data["count"]
        print(f"✓ dish-images-list returns {data['count']} images for {slug}")


class TestPutDishEndpoint:
    """Test PUT /api/admin/dishes/{slug} endpoint"""
    
    def test_put_dish_updates_data(self):
        """Verify PUT updates dish data correctly"""
        slug = "arroz-branco"
        
        # First get current data
        get_response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        dishes = get_response.json().get("dishes", [])
        original_dish = next((d for d in dishes if d["slug"] == slug), None)
        assert original_dish is not None
        
        original_desc = original_dish.get("descricao", "")
        test_desc = f"Test description {time.time()}"
        
        # Update with new description
        update_payload = {
            "descricao": test_desc
        }
        put_response = requests.put(f"{BASE_URL}/api/admin/dishes/{slug}", json=update_payload, timeout=30)
        assert put_response.status_code == 200
        data = put_response.json()
        assert data.get("ok") == True
        print(f"✓ PUT /api/admin/dishes/{slug} returned ok:true")
        
        # Verify update persisted
        get_response2 = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        dishes2 = get_response2.json().get("dishes", [])
        updated_dish = next((d for d in dishes2 if d["slug"] == slug), None)
        assert updated_dish.get("descricao") == test_desc
        print(f"✓ Description updated and persisted correctly")
        
        # Restore original description
        restore_payload = {"descricao": original_desc}
        requests.put(f"{BASE_URL}/api/admin/dishes/{slug}", json=restore_payload, timeout=30)
        print(f"✓ Original description restored")


class TestDeleteImageEndpoint:
    """Test DELETE /api/admin/dish-image/{slug}?img={img} endpoint"""
    
    def test_delete_nonexistent_image_returns_404(self):
        """Verify delete returns 404 for non-existent image"""
        slug = "arroz-branco"
        img = "imagem-que-nao-existe-xyz.jpg"
        
        response = requests.delete(f"{BASE_URL}/api/admin/dish-image/{slug}?img={img}", timeout=30)
        # Should return 404 or error
        assert response.status_code in [404, 500]
        print(f"✓ Delete non-existent image returns {response.status_code}")


class TestCloudAndLocalImages:
    """Test hybrid cloud/local image storage"""
    
    def test_cloud_storage_image(self):
        """Verify cloud storage image (abobora-ao-curry) loads correctly"""
        slug = "abobora-ao-curry"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=30)
        
        assert response.status_code == 200
        assert len(response.content) > 5000  # Should be valid image
        print(f"✓ Cloud storage image: {len(response.content)/1024:.1f}KB")
    
    def test_local_fallback_image(self):
        """Verify local fallback image loads correctly"""
        slug = "frango-ao-creme-de-limao"
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/{slug}?thumb=1", timeout=30)
        
        assert response.status_code == 200
        assert len(response.content) > 5000  # Should be valid image
        print(f"✓ Local fallback image: {len(response.content)/1024:.1f}KB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
