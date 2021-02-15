import React, { useContext } from 'react';
import { HunnyduContext } from './Context/index';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Spinner from 'react-bootstrap/Spinner';


// Component to handle confirming a members invitation token.
// Component is accessed by a link sent in a confirmation email.
const ConfirmUser = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare dynamic url token.
  const {match} = props
  const token = match.params.token;


  // Method to handle confirming the provided token.
  // User is always directed to '/' after processing.
  actions.confirmConfirmationToken(token)
    .then(res => {
      if (res) {
        if (res.status === 200) {
          // Returned response is code 200 for successful confirmation.
          console.log('Successful confirmation.');
        }
        else if (res.status === 202) {
          // Returned response is code 202 for user previously confirmed.
          console.log('User previously confirmed.');
        }
      } else {
        // Returned response is code 401 for unauthorized (invalid token).
        console.log('Failed confirmation!');
      }
      props.history.push('/login');
    })


  // Return component jsx.
  // Component renders a loading wheel until redirected.
  return(
    <Container className="loginForm-container">
      <Col lg>
        <Row className="justify-content-md-center">
          <Spinner animation="grow" role="status">
            <span className="sr-only">Loading...</span>
          </Spinner>
        </Row>
      </Col>
    </Container>
  );
}


export default ConfirmUser;
