# Formspree Integration Setup Guide

## Overview
The contact form in the Help page uses Formspree to send emails to your official email address. All form submissions are automatically forwarded to your configured email.

## Setup Steps

### 1. Create a Formspree Account
1. Go to [https://formspree.io](https://formspree.io)
2. Sign up for a free account (or log in if you already have one)
3. The free plan includes 50 submissions per month

### 2. Create a New Form
1. After logging in, click "New Form" or "Create Form"
2. Give your form a name (e.g., "VIRO-AI Contact Form")
3. Formspree will generate a unique form ID (looks like: `xvgwqkny`)

### 3. Configure Your Form
1. **Set the recipient email**: 
   - Go to your form settings
   - Under "Email Notifications", add your official email address
   - This is where all form submissions will be sent

2. **Configure reply-to**:
   - Enable "Reply-To" in form settings
   - This allows you to reply directly to the user's email

3. **Optional settings**:
   - Enable email notifications
   - Set up custom subject lines
   - Add spam protection (reCAPTCHA)

### 4. Get Your Form ID
1. In your Formspree dashboard, click on your form
2. You'll see the form endpoint: `https://formspree.io/f/YOUR_FORM_ID`
3. Copy the form ID (the part after `/f/`)

### 5. Update the Code
1. Open `workspace/shadcn-ui/src/pages/dashboard/Help.tsx`
2. Find the line: `<ContactForm formspreeId="YOUR_FORMSPREE_ID" />`
3. Replace `YOUR_FORMSPREE_ID` with your actual Formspree form ID

Example:
```tsx
<ContactForm formspreeId="xvgwqkny" />
```

### 6. Test the Form
1. Navigate to the Help page in your application
2. Fill out and submit the contact form
3. Check your email inbox for the form submission
4. Verify that you can reply to the user's email

## How It Works

1. **User submits form** → Form data is sent to Formspree
2. **Formspree processes** → Validates and formats the submission
3. **Email sent** → You receive an email at your configured address
4. **Reply capability** → You can reply directly to the user's email

## Form Fields

The contact form includes:
- **Name**: User's name (required)
- **Email**: User's email address (required) - used for replies
- **Subject**: Message subject (required)
- **Project ID**: Optional project reference
- **Message**: Detailed message content (required)

## Customization

### Change the Official Email
- Update the email in your Formspree form settings
- No code changes needed

### Add More Fields
Edit `workspace/shadcn-ui/src/components/ContactForm.tsx`:
1. Add the field to the `formData` state
2. Add the input in the JSX
3. Include it in the Formspree submission body

### Change Form Location
The form is currently in the Help page. You can also use it in other pages:
```tsx
import ContactForm from '@/components/ContactForm';

// In your component:
<ContactForm formspreeId="YOUR_FORM_ID" />
```

## Troubleshooting

### Form not submitting?
- Check that your Formspree ID is correct
- Verify your Formspree account is active
- Check browser console for errors
- Ensure you haven't exceeded the free plan limit (50/month)

### Not receiving emails?
- Check your Formspree form settings
- Verify the recipient email is correct
- Check spam/junk folder
- Ensure email notifications are enabled in Formspree

### Need more submissions?
- Upgrade to Formspree Pro plan
- Or create multiple forms for different purposes

## Security Notes

- Formspree handles spam protection
- All submissions are encrypted in transit
- User emails are kept private
- No sensitive data should be collected via this form

## Support

For Formspree-specific issues:
- Visit [Formspree Documentation](https://help.formspree.io/)
- Contact Formspree support

For code-related issues:
- Check the component code in `src/components/ContactForm.tsx`
- Review the Help page integration in `src/pages/dashboard/Help.tsx`

