export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'coffee-shop-lb.eu', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: '4Deg6Q023h7WJhx2CNNkZHT4kSfGI5f0', // the client id generated for the auth0 app
    callbackURL: 'https://127.0.0.1:4200', // the base url of the running ionic application.
  }
};
