import React from 'react';
import Jumbotron from 'react-bootstrap/Jumbotron';


// Component that will display for url's not listed in the router.
const NotFound = () => (
  <Jumbotron>
    <h1>Page Not Found :( .</h1>
  </Jumbotron>
);


export default NotFound;
