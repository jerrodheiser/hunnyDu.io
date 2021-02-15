import React, { useState } from 'react';
import Data from '../Data/index';
import Cookies from 'js-cookie';

export const HunnyduContext = React.createContext();

// Context API for the application.
export const Provider = (props) => {

  // Declares the tasks state for the session.
  // This state will be updated any time a change is made to the api using
  //  refreshTasks().
  const [tasks, setTasks] = useState();

  // Declares the family tasks state for the session.
  // This state will be updated any time a change is made to the api using
  //  refreshTasks().
  const [familyTasks, setFamilyTasks] = useState();

  // Declares the family name for the session.
  const [familyName, setFamilyName] = useState(Cookies.getJSON('familyName'));

  // Declares the members list for the session.
  const [members, setMembers] = useState(Cookies.getJSON('members'));

  // Declares if the user is a leader for the session.
  const [isLeader, setIsLeader] = useState(Cookies.getJSON('isLeader'));

  // Declares how many leaders are in a users family for the session.
  const [leaders, setLeaders] = useState(Cookies.getJSON('leaders'));

  // Declare the users ID for the session.
  const [id, setId] = useState(Cookies.getJSON('id'));

  // Declares the authenticated state for the context.
  const [isAuthenticated, setIsAuthenticated] = useState(() =>{
      if (Cookies.getJSON('apiToken')) {
        return true;
      } else {
        return false;
      }
    });

  // Import the functions from the data module.
  const data = new Data();


  // Method to login a user, and populate cookies with session data.
  const loginUser = (email, password) => {
    const response = data.getUser(email, password);
    response.then(res => {
      if (res.status === 200 && res.data.confirmed) {
        Cookies.set('apiToken', JSON.stringify(res.data.token), {expires:1});
        setIsAuthenticated(true);
        Cookies.set('familyName', JSON.stringify(res.data.family_name), {expires:1});
        setFamilyName(res.data.family_name);
        Cookies.set('members', JSON.stringify(res.data.members), {expires:1});
        setMembers(res.data.members);
        Cookies.set('isLeader', JSON.stringify(res.data.isLeader), {expires:1});
        setIsLeader(res.data.isLeader);
        Cookies.set('leaders', JSON.stringify(res.data.leaders), {expires:1});
        setIsLeader(res.data.leaders);
        Cookies.set('id', JSON.stringify(res.data.id), {expires:1});
        setId(res.data.id);
      }
      else if (res.status === 200) {
        Cookies.set('id', JSON.stringify(res.data.id), {expires:1});
        setId(res.data.id);
        Cookies.remove('apiToken');
        setIsAuthenticated(false);
      }
      else {
        Cookies.remove('apiToken');
        setIsAuthenticated(false);
      }
    });
    return response;
  }


  // Method to register new user information.
  const registerUser = (username, email, password) => {
    const response = data.api('/api/auth/registration', 'post', {
        username: username,
        email: email,
        password: password
      }, true, {email_or_token: null})
      .catch(err => {
        return err;
      });
    return response;
  }


  // Method to update a new user's profile as confirmed.
  const confirmConfirmationToken = (token)  => {
    const response = data.api(`/api/auth/confirmUser/${token}`, 'post', null,
      true, {email_or_token: null})
      .catch(err => console.log(err));
    return response;
  }


  // Method to resend a confirmation email.
  const resendConfirmationEmail = (userId) => {
    data.api(`/api/auth/resendConfirmationEmail`, 'post', {id: userId},
      true, {email_or_token: null})
      .catch(err => console.log(err))
  }


  // Methods to confirm a provided invite token.
  const confirmInviteToken = (token)  => {
    const response = data.api(`/api/auth/confirmInviteToken/${token}`, 'post', null,
      true, {email_or_token: null})
      .catch(err => console.log(err));
    response.then(res => {
      if (res) {
        if (res.status === 200) {
          refreshFamily();
        }
      }
    });
    return response;
  }


  // Method to send an email request to join a family.
  const sendFamilyInvite = (email) => {
    data.api('/api/auth/sendFamilyInvite', 'post',{
      email:email}, true, {email_or_token: Cookies.getJSON('apiToken')});
  }


  // Method to obtain a password reset token.
  const sendResetRequest = (email) => {
    data.api('/api/auth/sendResetRequest','post', {
      email:email}, true, {email_or_token: null})
      .catch(err => console.log(err));
  }


  // Method to validate a reset password request token, and then render the
  //  reset password form.
  const validateResetRequest = (token) => {
    const response = data.api(`/api/auth/validateResetRequest/${token}`, 'post',
      null, true, {email_or_token: null})
      .catch(err => console.log(err));
    return response;
  }


  // Method to reset a users password.
  const resetPassword = (password, token) => {
    const response = data.api('/api/auth/processPasswordReset','post', {
      password: password, token: token}, true, {email_or_token: null})
      .catch(err => console.log(err));
    return response;
  }


  // Method to refresh the tasks and familyTasks state variables.
  // Called after every post request to the database.
  const refreshTasks = () => {
    const response = data.api('/api/getTasks','post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
      .then(response => {
        setTasks(response.data.tasks);
        setFamilyTasks(response.data.familyTasks);
      })
      .catch(err => logoutUser());
    return response;
  };


  // Method to get user profile page information.
  const getProfile = (id) => {
    const response = data.api(`/api/users/${id}`, 'post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.log(err));
    return response;
  }


  // Method to add a new task.
  const handleAddTask = (task) => {
    data.api('/api/tasks','post',{
        taskname:task.taskname,
        period:task.period,
        assignee:task.assignee,
        subtasks:task.subtasks,
      }, true,
      {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(()=>refreshTasks());
  }


  // Method to complete/uncomplete a subtask.
  const handleSubtaskComplete = (si) => {
    data.api(`/api/change_subtask_complete/${si}`,'post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(()=>refreshTasks());
  };


  // Method to add a new subtask.
  const handleAddSubtask = (ti, stName) => {
    data.api(`/api/add_subtask/${ti}`,'post', {
      subtask_name: stName
    }, true, {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(()=>refreshTasks());
  }


  // Method to delete a task and its associated subtasks.
  const handleDeleteTask = (ti) => {
    data.api(`/api/delete_task/${ti}`,'post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
    .catch(err => console.error(err))
    .finally(()=>refreshTasks());
  }


  // Method to delete a subtask.
  const handleDeleteSubtask = (si) => {
    data.api(`/api/delete_subtask/${si}`,'post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(()=>refreshTasks());
  }


  // Method to remove a member from a family, and remove associated tasks.
  const removeFamilyMember = (id) => {
    data.api('/api/auth/removeFamilyMember', 'post', {id:id}, true,
        {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(() => refreshFamily());
  }


  // Method to give a user leader permissions.
  const makeLeader = (id) => {
    data.api('/api/auth/makeLeader', 'post', {id:id}, true,
        {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(res => {
        refreshFamily();
      });
  }


  // Method to remove a user leader permissions.
  const unmakeLeader = (id) => {
    data.api('/api/auth/unmakeLeader', 'post', {id:id}, true,
        {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err))
      .finally(() => refreshFamily());
  }


  // Method to send a change email token to the new desired email address.
  const sendChangeEmailRequest = (email) => {
    data.api('/api/auth/changeEmailRequest', 'post', {email:email},
      true, {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err));
  }


  // Method to confirm a user's new email address.
  const confirmChangeEmail = (token) => {
    const response = data.api('/api/auth/confirmChangeEmail', 'post', {token:token},
      true, {email_or_token:null})
      .catch(err => console.error(err));
    return response;
  }


  // Method to refresh the tasks and familyTasks state variables.
  const refreshFamily = () => {
    const response = data.api('/api/auth/getFamily','post', null, true, {
      email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.error(err));
    response.then(res => {
      if (res.status === 200) {
        Cookies.set('familyName', JSON.stringify(res.data.family_name), {expires:1})
        setFamilyName(res.data.family_name);
        Cookies.set('members', JSON.stringify(res.data.members), {expires:1})
        setMembers(res.data.members);
        Cookies.set('leaders', JSON.stringify(res.data.leaders), {expires:1})
        setIsLeader(res.data.leaders);
        Cookies.set('isLeader', JSON.stringify(res.data.isLeader), {expires:1})
        setIsLeader(res.data.isLeader);
      }
    });
  }


  // Method to create a new family.
  const createFamily = (name) => {
    const response = data.api('/api/auth/createFamily','post', {familyName: name},
      true, {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.log(err));
    return response;
  }


  // Method to send a password change request.
  const changePassword = (oldPass, newPass) => {
    const response = data.api('/api/auth/changePassword', 'post', {
      oldPass:oldPass, newPass:newPass}, true,
      {email_or_token: Cookies.getJSON('apiToken')})
      .catch(err => console.log(err));
    return response;
  }


  // Method to logout a user and reset session variables.
  const logoutUser = () => {
    Cookies.remove('apiToken');
    Cookies.remove('members');
    Cookies.remove('isLeader');
    Cookies.remove('leaders');
    Cookies.remove('familyName');
    Cookies.remove('id');
    setTasks(null);
    setFamilyTasks(null);
    setMembers(null);
    setIsAuthenticated(false);
    setIsLeader(null);
    setLeaders(null);
    setId(null);
  }


  // Provide children to the application.
  return (
    <HunnyduContext.Provider
      value={{
        tasks: tasks,
        familyTasks:familyTasks,
        isAuthenticated: isAuthenticated,
        familyName: familyName,
        id: id,
        members: members,
        isLeader:isLeader,
        leaders: leaders,
        actions: {
          addSubtask: handleAddSubtask,
          subtaskComplete: handleSubtaskComplete,
          addTask: handleAddTask,
          refreshTasks: refreshTasks,
          deleteSubtask: handleDeleteSubtask,
          deleteTask: handleDeleteTask,
          loginUser: loginUser,
          logoutUser: logoutUser,
          registerUser: registerUser,
          resendConfirmationEmail: resendConfirmationEmail,
          sendFamilyInvite: sendFamilyInvite,
          confirmConfirmationToken: confirmConfirmationToken,
          confirmInviteToken: confirmInviteToken,
          sendResetRequest: sendResetRequest,
          validateResetRequest: validateResetRequest,
          resetPassword: resetPassword,
          removeFamilyMember: removeFamilyMember,
          refreshFamily: refreshFamily,
          unmakeLeader: unmakeLeader,
          makeLeader: makeLeader,
          getProfile: getProfile,
          sendChangeEmailRequest: sendChangeEmailRequest,
          confirmChangeEmail: confirmChangeEmail,
          createFamily: createFamily,
          changePassword: changePassword
        }
      }}>
      {props.children}
    </HunnyduContext.Provider>
    );
}

export const Consumer = HunnyduContext.Consumer;
