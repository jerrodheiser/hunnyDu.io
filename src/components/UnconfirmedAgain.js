import React, {useContext} from 'react';
import {HunnyduContext} from './Context/index';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';

// Component that will display for unconfirmed users.
const UnconfirmedAgain = () => {

  // Declare context api data.
  const {actions, id} = useContext(HunnyduContext);

  const handleClick = () => {
    console.log(id);
    actions.resendConfirmationEmail(id);
    console.log('Resent confirmation email.');
  }

  // Return component jsx.
  return (
    <Container>
      <Jumbotron>
        <h1>Please confirm your email address.</h1>
        <h2>Click below to resend the confirmation email.</h2>
      </Jumbotron>
      <Button type='success' onClick={() => handleClick()}> Resend </Button>
    </Container>
  );
}


export default UnconfirmedAgain;
