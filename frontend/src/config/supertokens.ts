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
    EmailPassword.init(),
    Session.init()
  ],
})

