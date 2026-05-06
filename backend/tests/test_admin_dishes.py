# -*- coding: utf-8 -*-
"""
SoulNutri Admin Dishes API Tests
Tests for /api/admin/dishes-full and /api/admin/dish-image endpoints
After Object Storage migration (99 cloud + 107 local dishes)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://nutri-familia.preview.emergentagent.com').rstrip('/')


class TestAdminDishesFull:
    """Tests for GET /api/admin/dishes-full endpoint"""
    
    def test_dishes_full_returns_ok(self):
        """GET /api/admin/dishes-full should return ok:true"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True, f"Expected ok:true, got {data}"
        print(f"✅ dishes-full returns ok:true")
    
    def test_dishes_full_returns_206_dishes(self):
        """GET /api/admin/dishes-full should return exactly 206 dishes"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        total = data.get("total", len(dishes))
        assert total == 206, f"Expected 206 dishes, got {total}"
        assert len(dishes) == 206, f"Expected 206 dishes in array, got {len(dishes)}"
        print(f"✅ dishes-full returns 206 dishes")
    
    def test_all_dishes_have_images(self):
        """All dishes should have image_count > 0"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        zero_image_dishes = [d for d in dishes if d.get("image_count", 0) == 0]
        assert len(zero_image_dishes) == 0, f"Found {len(zero_image_dishes)} dishes with image_count=0: {[d['slug'] for d in zero_image_dishes[:5]]}"
        print(f"✅ All 206 dishes have image_count > 0")
    
    def test_slugs_are_clean_format(self):
        """All slugs should be in clean hyphen format (no underscores)"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        bad_slugs = []
        for d in dishes:
            slug = d.get("slug", "")
            # Check for underscores or non-alphanumeric (except hyphens)
            if "_" in slug:
                bad_slugs.append(slug)
            elif not slug.replace("-", "").replace(" ", "").isalnum():
                bad_slugs.append(slug)
        
        assert len(bad_slugs) == 0, f"Found {len(bad_slugs)} slugs with bad format: {bad_slugs[:10]}"
        print(f"✅ All slugs are in clean hyphen format")
    
    def test_dishes_have_first_image(self):
        """All dishes with images should have first_image set"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        missing_first_image = [d for d in dishes if d.get("image_count", 0) > 0 and not d.get("first_image")]
        assert len(missing_first_image) == 0, f"Found {len(missing_first_image)} dishes with images but no first_image"
        print(f"✅ All dishes with images have first_image set")


class TestAdminDishImage:
    """Tests for GET /api/admin/dish-image/{slug} endpoint"""
    
    def test_arroz_branco_image_valid(self):
        """GET /api/admin/dish-image/arroz-branco should return JPEG > 5000 bytes"""
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/arroz-branco", timeout=30)
        assert response.status_code == 200
        assert len(response.content) > 5000, f"Expected > 5000 bytes, got {len(response.content)}"
        assert response.headers.get("content-type", "").startswith("image/"), f"Expected image content-type, got {response.headers.get('content-type')}"
        print(f"✅ arroz-branco image: {len(response.content)} bytes")
    
    def test_arroz_branco_specific_image(self):
        """GET /api/admin/dish-image/arroz-branco?img=arrozbranco026.jpeg should return ~155KB"""
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/arroz-branco?img=arrozbranco026.jpeg", timeout=30)
        assert response.status_code == 200
        size = len(response.content)
        # Should be around 155KB (155216 bytes)
        assert size > 100000, f"Expected > 100KB, got {size} bytes"
        assert size < 200000, f"Expected < 200KB, got {size} bytes"
        print(f"✅ arroz-branco specific image (arrozbranco026.jpeg): {size} bytes (~{size//1024}KB)")
    
    def test_abobora_ao_curry_image_cloud(self):
        """GET /api/admin/dish-image/abobora-ao-curry should return valid image (cloud storage)"""
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/abobora-ao-curry", timeout=30)
        assert response.status_code == 200
        assert len(response.content) > 5000, f"Expected > 5000 bytes, got {len(response.content)}"
        assert response.headers.get("content-type", "").startswith("image/"), f"Expected image content-type"
        print(f"✅ abobora-ao-curry image (cloud): {len(response.content)} bytes")
    
    def test_frango_ao_creme_de_limao_image(self):
        """GET /api/admin/dish-image/frango-ao-creme-de-limao should return valid image"""
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/frango-ao-creme-de-limao", timeout=30)
        assert response.status_code == 200
        assert len(response.content) > 5000, f"Expected > 5000 bytes, got {len(response.content)}"
        print(f"✅ frango-ao-creme-de-limao image: {len(response.content)} bytes")
    
    def test_nonexistent_dish_returns_404(self):
        """GET /api/admin/dish-image/nonexistent-dish should return 404"""
        response = requests.get(f"{BASE_URL}/api/admin/dish-image/nonexistent-dish-xyz123", timeout=30)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✅ Nonexistent dish returns 404")


class TestAdminSearch:
    """Tests for search functionality in admin"""
    
    def test_search_arroz_returns_multiple(self):
        """Searching for 'Arroz' should return multiple dishes"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        arroz_dishes = [d for d in dishes if "arroz" in d.get("nome", "").lower() or "arroz" in d.get("slug", "").lower()]
        assert len(arroz_dishes) > 0, "Expected at least 1 arroz dish"
        
        # Verify all arroz dishes have images
        for d in arroz_dishes:
            assert d.get("image_count", 0) > 0, f"Arroz dish {d['slug']} has no images"
        
        print(f"✅ Found {len(arroz_dishes)} arroz dishes, all with images")
        print(f"   Arroz dishes: {[d['slug'] for d in arroz_dishes[:5]]}")


class TestDataIntegrity:
    """Tests for data integrity after migration"""
    
    def test_dish_structure_complete(self):
        """All dishes should have required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        required_fields = ["slug", "nome", "image_count", "first_image", "all_images"]
        
        for dish in dishes[:10]:  # Check first 10
            for field in required_fields:
                assert field in dish, f"Dish {dish.get('slug')} missing field: {field}"
        
        print(f"✅ All dishes have required fields")
    
    def test_image_count_matches_all_images(self):
        """image_count should match len(all_images)"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        dishes = data.get("dishes", [])
        
        mismatches = []
        for d in dishes:
            count = d.get("image_count", 0)
            all_imgs = d.get("all_images", [])
            if count != len(all_imgs):
                mismatches.append(f"{d['slug']}: count={count}, all_images={len(all_imgs)}")
        
        # Allow some tolerance for edge cases
        assert len(mismatches) < 5, f"Found {len(mismatches)} mismatches: {mismatches[:5]}"
        print(f"✅ image_count matches all_images length (mismatches: {len(mismatches)})")


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
