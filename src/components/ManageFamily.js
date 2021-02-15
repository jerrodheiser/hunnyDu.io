import React, {useContext, useEffect} from 'react';
import {HunnyduContext} from './Context/index';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';


// Component that allows for managing the user's family.
const ManageFamily = () => {

  // Declare context api data.
  const {members, actions, familyName} = useContext(HunnyduContext);

  // Refreshes family information on initial render.
  useEffect (() => {
    actions.refreshFamily();
  },[]);

  // Method to handle removing a family member.
  const handleRemove = (id) => {
    actions.removeFamilyMember(id);
  }

  // Method to handle adding leader permissions to a user.
  const handleMakeLeader = (id) => {
    actions.makeLeader(id);
  }

  // Method to handle removing leader permissions to a user.
  const handleUnmakeLeader = (id) => {
    actions.unmakeLeader(id);
  }


  // Return component jsx.
  return (
    <Container>
      <h1 className="pageTitle" >
        {familyName} - Manage Family
      </h1>
      {members.map( (member, index) =>
        <Container key={index.toString()}>
          <Card bg='light'>
            <Row>
              <Col>
                <Card.Body>
                  <a href={`/viewProfile/${member.id}`}>
                    {member.name}</a>
                </Card.Body>
              </Col>
              {member.isLeader
                ?
                  member.isOnlyLeader
                    ? ''
                    :
                      <Col xs lg="2" className="center-aligned">
                        <Button
                        variant='danger'
                        block
                        onClick={() => handleUnmakeLeader(member.id)}>
                          Unmake Leader
                        </Button>
                      </Col>
                :
                  <>
                    <Col xs lg="2" className="center-aligned">
                      <Button
                      variant='success'
                      block
                      onClick={() => handleMakeLeader(member.id)}>
                      Make Leader
                      </Button>
                    </Col>
                    <Col xs lg="2" className="center-aligned">
                      <Button
                      variant='danger'
                      block
                      onClick={() => handleRemove(member.id)}>
                        Remove
                      </Button>
                    </Col>
                  </>
              }
            </Row>
          </Card>
        </Container>
      )}
    </Container>
  );
}


export default ManageFamily;
