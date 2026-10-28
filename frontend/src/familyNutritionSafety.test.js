import {
  canUseSpecificNutrition,
  getFamilySafeDisplayName,
  isFamilyMemberConfirmationPending,
} from './familyNutritionSafety';

const ambiguousCanelone = {
  dish: 'canelonedeespinafre',
  dish_display: 'Canelone de Espinafre',
  family_name: 'Canelone',
  family_member_confirmation_required: true,
  family_member_confirmed: false,
  specific_nutrition_authorized: false,
};

test('family pending confirmation is displayed as the family, not the top-1 member', () => {
  expect(isFamilyMemberConfirmationPending(ambiguousCanelone)).toBe(true);
  expect(getFamilySafeDisplayName(ambiguousCanelone)).toBe('Canelone');
  expect(canUseSpecificNutrition(ambiguousCanelone)).toBe(false);
});

test('existing families without the opt-in flag preserve their current behavior', () => {
  const pastel = {
    dish: 'pastel',
    dish_display: 'Pastel',
    family_name: 'Pastéis',
    specific_nutrition_authorized: true,
  };
  expect(isFamilyMemberConfirmationPending(pastel)).toBe(false);
  expect(getFamilySafeDisplayName(pastel)).toBe('Pastel');
  expect(canUseSpecificNutrition(pastel)).toBe(true);

  const gratinados = {
    dish_display: 'Brócolis Gratinado',
    family_name: 'Gratinados',
    family_slug: 'gratinados',
  };
  expect(getFamilySafeDisplayName(gratinados)).toBe('Gratinados');
  expect(canUseSpecificNutrition(gratinados)).toBe(true);
});

test('the shared gate keeps scanner and persistence projections family-only', () => {
  const serverPayload = {
    ...ambiguousCanelone,
    nutrition: null,
    ingredientes: [],
    alergenos: {},
  };
  const scannerProjection = {
    dish_display: getFamilySafeDisplayName(serverPayload),
    calorias: canUseSpecificNutrition(serverPayload) ? '~150 kcal' : '—',
  };
  expect(scannerProjection).toEqual({ dish_display: 'Canelone', calorias: '—' });
  expect(canUseSpecificNutrition(serverPayload)).toBe(false);
});
