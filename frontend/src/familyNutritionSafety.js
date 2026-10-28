export const isFamilyMemberConfirmationPending = (result) => Boolean(
  result?.family_member_confirmation_required &&
  result?.family_member_confirmed !== true
);

export const getFamilySafeDisplayName = (result) => {
  if (isFamilyMemberConfirmationPending(result) && result?.family_name) {
    return result.family_name;
  }
  const legacyFamilyTitleSlugs = new Set([
    'milanesa',
    'batata',
    'sobrecoxa',
    'gratinados',
  ]);
  if (
    result?.family_name &&
    legacyFamilyTitleSlugs.has(String(result?.family_slug || '').toLowerCase())
  ) {
    return result.family_name;
  }
  return result?.dish_display || result?.dish || '';
};

export const canUseSpecificNutrition = (result) => (
  !isFamilyMemberConfirmationPending(result) &&
  result?.specific_nutrition_authorized !== false
);
