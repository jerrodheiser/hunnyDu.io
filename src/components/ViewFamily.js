import React, {useContext, useEffect} from 'react';
import {HunnyduContext} from './Context/index';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';


// Component that displays a user's family.
const ViewFamily = () => {

  // Declare context api data.
  const {members, actions, familyName} = useContext(HunnyduContext);


  // Refreshes family information on initial render.
  useEffect (() => {
    actions.refreshFamily();
  },[]);


  // Return component jsx.
  return (
    <Container>
      <h1 className="pageTitle" >
        {familyName} - Family Roster
      </h1>
      {members.map( (member, index) =>
        <Container key={index.toString()}>
          <Card bg='light'>
            <Card.Body>
              <a href={`/viewProfile/${member.id}`}>
                {member.name} {member.isLeader ? '(leader)' : ''}</a>
            </Card.Body>
          </Card>
        </Container>
      )}
    </Container>
  );
}


export default ViewFamily;
