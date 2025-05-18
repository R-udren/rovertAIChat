// Validation schemas using Zod
import { z } from 'zod'

// User profile schema
export const profileSchema = z.object({
  username: z
    .string({ required_error: 'Username is required' })
    .min(4, { message: 'Username must be at least 4 characters' })
    .max(100, { message: 'Username cannot exceed 100 characters' }),
  email: z
    .string({ required_error: 'Email is required' })
    .email({ message: 'Please enter a valid email address' }),
  avatar_url: z
    .string()
    .url({ message: 'Please enter a valid URL' })
    .max(255, { message: 'URL cannot exceed 255 characters' })
    .optional()
    .or(z.literal('')), // Allow empty string
})

// Validate a form field with real-time feedback
export const validateField = (schema, field, value) => {
  // If the field is optional and empty, return valid
  if (
    (value === '' || value === undefined) &&
    (field === 'avatar_url' || schema.shape[field].isOptional?.() === true)
  ) {
    return { valid: true, message: '' }
  }

  try {
    // Create a partial schema with just the field we're validating
    const fieldSchema = z.object({ [field]: schema.shape[field] })
    fieldSchema.parse({ [field]: value })
    return { valid: true, message: '' }
  } catch (error) {
    const message = error.errors?.[0]?.message || `Invalid ${field}`
    return { valid: false, message }
  }
}

// Full form validation
export const validateForm = (schema, data) => {
  try {
    schema.parse(data)
    return { valid: true, errors: {} }
  } catch (error) {
    const errors = {}
    error.errors.forEach((err) => {
      // Get the field name from the path
      const field = err.path[0]
      errors[field] = err.message
    })
    return { valid: false, errors }
  }
}
