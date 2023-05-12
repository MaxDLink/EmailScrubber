## This is the README.md file 
 # how do I pipe the reprompt back through AgentGPT so that AgentGPT can make an alteration instead of rewriting it <-- this is key <-- make this work with CHATGPT 4 model instead of 3.5 
 # how do I add other functionality like sorting email inbox? 
 # how do I make this an extension? 


## Current Tasks  

# set up prompt engineering - model after randeer on git hub: https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor/blob/main/Mr_Ranedeer.json#L86 

# refine the prompt with the ChatGPT conversational model. Use ChatGPT 4? Determine if AgentGPT is in usage while you just write emails. Also either have ChatGPT write the prompt for you or do not have ChatGPT write the prompt. Need to be able to switch languages. 
# have email_helper monitor the email inbox - label emails, move emails to trash, schedule appointments - all passively from no user input 



# model user interface after twitter extension:https://github.com/recalign/RecAlign/blob/main/README.md 

# send email to multiple people at once. 
# user interface 

# Testing/bugs 

# ability to unsubscribe from gmails in mass? <--- Later 


# ship basic v1 


## Security to follow when using full GMAIL API: 

Using the full Gmail API scope ('https://mail.google.com/') grants your application extensive permissions, so it is crucial to follow security best practices to protect user data and maintain the security of your application. Some recommended practices include:

Store credentials securely: Keep your API keys, client secrets, and access tokens in a secure location. Avoid hardcoding these values into your code. Use environment variables, configuration files, or secret management systems to securely store sensitive information.

Limit access: Restrict access to your application's credentials and tokens to only the necessary individuals and services. Implement the principle of least privilege, providing the minimum level of access needed for each user or service.

Regularly review and update permissions: Periodically review and update the permissions granted to your application. Remove any unnecessary scopes to minimize potential security risks.

Use HTTPS: Always use HTTPS when communicating with external services and transmitting sensitive data. This ensures that data is encrypted during transit, protecting it from unauthorized access.

Implement access and refresh tokens: Access tokens typically have a short lifespan, while refresh tokens can be used to obtain new access tokens when they expire. Implementing refresh tokens helps maintain the security of your application by limiting the duration of access tokens.

Monitor and audit: Regularly monitor and audit your application's usage of the Gmail API. This can help identify any potential security breaches or misuse of the API.

Keep your code and dependencies up-to-date: Regularly update your application's code and dependencies to ensure that you are using the latest security patches and best practices.

Educate users: Make sure your users are aware of the permissions they are granting to your application and inform them about how their data will be used. Encourage users to follow security best practices, such as using strong, unique passwords and enabling two-factor authentication.

Secure your server and infrastructure: Make sure the servers and infrastructure hosting your application are secure. Implement strong access controls, keep software up-to-date, and monitor for potential vulnerabilities or breaches.

Validate and sanitize user input: Always validate and sanitize user input to protect your application against potential attacks, such as SQL injection or cross-site scripting (XSS).

By following these best practices, you can help minimize the security risks associated with using the full Gmail API scope and protect your users' data.