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
  display_name: z
    .string()
    .max(100, { message: 'Display name cannot exceed 100 characters' })
    .optional()
    .or(z.literal('')),
  avatar_url: z
    .string()
    .url({ message: 'Please enter a valid URL' })
    .max(255, { message: 'URL cannot exceed 255 characters' })
    .optional()
    .or(z.literal('')), // Allow empty string
})

// Login form schema
export const loginSchema = z.object({
  username: z
    .string({ required_error: 'Username is required' })
    .min(1, { message: 'Username is required' }),
  password: z
    .string({ required_error: 'Password is required' })
    .min(1, { message: 'Password is required' }),
})

// Registration form schema
export const registerSchema = z
  .object({
    username: z
      .string({ required_error: 'Username is required' })
      .min(4, { message: 'Username must be at least 4 characters' })
      .max(64, { message: 'Username cannot exceed 64 characters' }),
    email: z
      .string({ required_error: 'Email is required' })
      .email({ message: 'Please enter a valid email address' }),
    password: z
      .string({ required_error: 'Password is required' })
      .min(8, { message: 'Password must be at least 8 characters long' }),
    confirmPassword: z.string({ required_error: 'Please confirm your password' }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

// User settings schema
export const userSettingsSchema = z.object({
  default_model_id: z.string().optional().or(z.literal('')),
  preferences: z
    .object({
      theme: z.enum(['dark', 'light', 'system']),
      fontSize: z.enum(['small', 'medium', 'large']),
      chatBubbleStyle: z.enum(['rounded', 'square', 'modern']),
      messageSound: z.boolean(),
      notifications: z.boolean(),
    })
    .optional()
    .nullable(),
})

// Validate a form field with real-time feedback
export const validateField = (schema, field, value, allValues = {}) => {
  // Handle special cases for schemas with refinements
  if (!schema.shape && schema._def?.schema?.shape) {
    // For schemas with refinements, extract the base schema
    schema = schema._def.schema
  }

  // If the field is optional and empty, return valid
  if (
    (value === '' || value === undefined) &&
    (field === 'avatar_url' || schema.shape[field]?.isOptional?.() === true)
  ) {
    return { valid: true, message: '' }
  }

  try {
    // If we're validating a refined field (like confirmPassword)
    if (field === 'confirmPassword' && allValues.password) {
      // For password confirmation, we need to validate against the main schema
      // First validate the basic field structure
      if (schema.shape[field]) {
        const fieldSchema = z.object({ [field]: schema.shape[field] })
        fieldSchema.parse({ [field]: value })
      }

      // Then check if passwords match
      if (value !== allValues.password) {
        return { valid: false, message: "Passwords don't match" }
      }
    } else {
      // Normal field validation
      const fieldSchema = z.object({ [field]: schema.shape[field] })
      fieldSchema.parse({ [field]: value })
    }

    return { valid: true, message: '' }
  } catch (error) {
    const message = error.errors?.[0]?.message || error.message || `Invalid ${field}`
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

    if (error.errors && Array.isArray(error.errors)) {
      error.errors.forEach((err) => {
        // Get the field name from the path
        const field = err.path?.[0] || 'general'
        errors[field] = err.message
      })
    } else if (error.message) {
      // Handle simple error message
      errors.general = error.message
    }

    return { valid: false, errors }
  }
}
