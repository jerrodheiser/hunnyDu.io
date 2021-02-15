import React from 'react';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Container from 'react-bootstrap/Container';


// Component that will display for unconfirmed users after registration.
const UnconfirmedFirst = () => (
  <Container>
    <Jumbotron>
      <h1>Please check your email for a confirmation token.</h1>
    </Jumbotron>
  </Container>
);


export default UnconfirmedFirst;
