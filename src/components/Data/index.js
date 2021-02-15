import Cookies from 'js-cookie';
const axios = require('axios').default;


// This class will have methods which are used for interactions with the backend:
//  -API function
//  -login user function
export default class Data {

  // Method to process all api requests.
  api(path, method="get", body=null, requiresAuth = false, credentials = {}) {
    // Create request headers.
    const headers = {
      'Content-Type': 'application/json; charset=utf-8'
    };

    // Create request data.
    const data = {};

    // This will encode the credentials provided to the Authorization header.
    // BUGZ: Currently encodes credentials in the body.
    if ( requiresAuth ) {
      data.auth = {
        email_or_token: credentials.email_or_token || Cookies.getJSON('apiToken') || '',
        password: credentials.password,
      }
    }

    // Populate the body of the request if data is provided.
    if (body !== null) {
      data.body = JSON.stringify(body);
    }

    // Since GET requests cannot send data, this logic is performed to
    //    prevent a 400 error code (bad request) from occurring.
    if (method === 'get') { return axios.get(path) }
    else if (method === 'post') { return axios.post(path, data, headers) }
  }


  // Method to send user credentials for user login.
  async getUser(email, password) {
    const response = await this.api('/api/auth/login', 'post', null, true, {
        email_or_token:email,
        password: password})
      .catch(err => { return err; });
    return response;
  }
}
