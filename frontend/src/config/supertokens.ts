import SuperTokens from "supertokens-auth-react"
import EmailPassword from "supertokens-auth-react/recipe/emailpassword"
import Session from "supertokens-auth-react/recipe/session"

SuperTokens.init({
  appInfo: {
    appName: "Order Tracker",
    apiDomain: "http://localhost:8000",
    websiteDomain: "http://localhost:3000",
    apiBasePath: "/auth",
  },
  recipeList: [
    EmailPassword.init({
      signInAndUpFeature: {
        signUpForm: {
          formFields: [{
            id: "email",
            label: "Email",
            placeholder: "Enter your email"
          }, {
            id: "password",
            label: "Password",
            placeholder: "Enter your password"
          }]
        },
        signInForm: {
          formFields: [{
            id: "email",
            label: "Email",
            placeholder: "Enter your email"
          }, {
            id: "password",
            label: "Password",
            placeholder: "Enter your password"
          }]
        }
      },
      getRedirectionURL: async (context) => {
        if (context.action === "SUCCESS") {
          if (context.isNewUser) {
            // New user signed up - redirect to dashboard
            return "/dashboard"
          } else {
            // Existing user signed in - redirect to dashboard
            return "/dashboard"
          }
        }
        return undefined
      }
    }),
    Session.init()
  ],
})

