// Simple form validation composable
import { computed, ref } from 'vue'

export function useFormValidation(schema) {
  const form = ref({})
  const errors = ref({})
  const isSubmitting = ref(false)

  // Simple validation - only check on submit
  const validate = () => {
    try {
      schema.parse(form.value)
      errors.value = {}
      return true
    } catch (error) {
      const newErrors = {}
      if (error.errors?.length) {
        error.errors.forEach((err) => {
          const field = err.path?.[0]
          if (field) {
            newErrors[field] = err.message
          }
        })
      }
      errors.value = newErrors
      return false
    }
  }

  // Check if form is valid (has no errors and required fields are filled)
  const isValid = computed(() => {
    return (
      Object.keys(errors.value).length === 0 &&
      Object.values(form.value).every((value) => value?.toString().trim() !== '')
    )
  })

  // Clear errors
  const clearErrors = () => {
    errors.value = {}
  }

  return {
    form,
    errors,
    isSubmitting,
    isValid,
    validate,
    clearErrors,
  }
}
