const loginFormDiv = document.getElementById('login-div');
const logoutDiv=document.getElementById('logout-div')
const loginBtn=document.getElementById('login-btn')
const logoutBtn = document.getElementById('logout-btn');
const addPoemBtn=document.getElementById('add-poem-btn')
const editPoemBtn=document.getElementById('edit-poem-btn')
const deletePoemBtn=document.getElementById('delete-poem-btn')
const deleteAllPoemBtn=document.getElementById('delete-all-poem-btn')
const allPoemTable=document.getElementById('show-all-poem')
const allOwnPoemTable=document.getElementById('show-all-own-poem')
const poemIDTable= document.getElementById('show-poem-by-id');
const restrictedDiv=document.getElementById('restricted-routes');
const conncetionStatus=window.navigator.onLine;


//console.log(document.cookie)
window.addEventListener("load",()=>{
    if('serviceWorker' in navigator){ // if your browser supports service worker
        navigator.serviceWorker.register('/sw.js',{
            scope: '/'
        }).then((registration)=>{
            console.log("Service worker is successfully registered.") //if registration is successful
        }).catch((error)=>{
            console.log("Service worker registration is failed"); // if registration fails
        })
    }else{
        console.log("Service worker is not supported by your browser.")
    }
});

onLoadFunc = () => {
    
    let valid;
    fetch('http://localhost:8180/valid', {
        method: 'GET',
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then((response) => {
        return response.text()
    }).then(res => {

        //in response if we get valid then it means we are logged in
        valid = extractXMLData(res, '<message>', '</message>');
        if (valid === 'valid') {
            loginFormDiv.style.display = "none" //hidden in the page
            logoutDiv.style.display = "block" //shown in the page
            loadRestrictedFunctions(); // viewing the restricted  in the webpage
        }else {
            //else we are not logged in
            loginFormDiv.style.display = "block"
            logoutDiv.style.display = "none"
        }
        
    })

    disableButtons(conncetionStatus);


}

logoutFunc = () => {
    //console.log(document.cookie);
    fetch('http://localhost:8180/logout', {
        method: 'GET',
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then(() => {
        document.cookie = ""
        location.reload()
    }).catch(err=>{
        console.log(err);
    })
}

loadRestrictedFunctions = () => {
    restrictedDiv.style.display="block"; //if we are valid user then we are showing this div in the page
}

//localhost:8180 --> rest api 
loginAPI = (email, password) => {
    //console.log(email);
    //console.log(password)
    let data = `<credential><email>${email}</email><password>${password}</password></credential>`
    fetch('http://localhost:8180/login', {
        method: 'POST',
        body: data,
        credentials: 'include'
    }).then(response => {
        return response.text()
    }).then(res => {
        //console.log(res);
        let msg = extractXMLData(res, '<message>', '</message>');
        if (msg === "Successful") {
            location.reload();
        } else {
            alert("Wrong Credentials");
            location.reload()
        }
    }).catch(err=>{
        console.log(err);
    })
}

getLoginData = () => {
    email = document.forms["login-data"]["email"].value; //extracting the email
    password = document.forms["login-data"]["password"].value; // extracting the password
    document.forms["login-data"].reset();
    if ((email != "") && (password != "")) {
        loginAPI(email, password);
    }
}

getAllPoem = ()=>{
    clearTableData();
    allPoemTable.innerHTML="<tr><th>poemID</th><th>Poem</th><th>email</th></tr>";
    
    fetch("http://localhost:8180/poem",{
        method: 'GET',
    }).then(response=>{
        return response.text();
    }).then(res=>{
        allPoemTable.style.display="block" //showing this table in the webpage
        //console.log(res); //initial response from rest api
        res=res.slice(res.indexOf("<Poem>"),res.lastIndexOf("</Poem>")+"</Poem>".length);
        //console.log(res); // extracting Poems 
        const poems=res.split(/\r?\n/); //making array of each poem
        //console.log(poems)

        for(let i=0;i<poems.length;i++){
            //console.log(poems[i])
            let poem=extractXMLData(poems[i],'<Poem>','</Poem>');
            //console.log(poem);
            let row=allPoemTable.insertRow(i+1); // adding a row in the table
            let cell1=row.insertCell(0); //creating column in that row
            let cell2=row.insertCell(1); //same
            let cell3=row.insertCell(2); //same
            cell1.innerHTML=`${extractXMLData(poem,"<poemID>","</poemID>")}` //extracting poemID and setting the value to html
            cell2.innerHTML=`${extractXMLData(poem,"<poem>","</poem>")}` //same
            cell3.innerHTML=`${extractXMLData(poem,"<email>","</email>")}` //same
        }
        allPoemTable.innerHTML+="<br>";
    
	
    })
}

getPoemByID = ()=>{
    clearTableData();
    poemIDTable.innerHTML="<tr><th>poemID</th><th>Poem</th><th>email</th></tr>";
    let totalRowCount=1;
    id = document.forms["search-poem-id"]["poemID"].value;
    //console.log(id);
    document.forms["search-poem-id"].reset();
    
    fetch(`http://localhost:8180/poem/${id}`,{
        method: 'GET',
    }).then(response=>{
        //console.log(response);
        //  console.log(response.body)
        return response.text(); //text method covert readable streams into text
    }).then(res=>{
        //console.log(res);
        poemIDTable.style.display="block" //showing the table in the page
        let poem=extractXMLData(res,'<Poem>','</Poem>'); 
        let row=poemIDTable.insertRow(totalRowCount); //creating row in the table
        let cell1=row.insertCell(0); // creating a column in the created row
        let cell2=row.insertCell(1); //same 
        let cell3=row.insertCell(2); //same
        cell1.innerHTML=`${extractXMLData(poem,"<poemID>","</poemID>")}` //extract poemID and setting it in the table html
        cell2.innerHTML=`${extractXMLData(poem,"<poem>","</poem>")}` //same
        cell3.innerHTML=`${extractXMLData(poem,"<email>","</email>")}` //same
        poemIDTable.innerHTML+="<br>";
    

    })
    
}

getAllOwnPoem = ()=>{
    clearTableData(); //hiding all the tables
    allOwnPoemTable.innerHTML="<tr><th>poemID</th><th>Poem</th><th>email</th></tr>";
    //console.log(totalRowCount);
    
    fetch("http://localhost:8180/poems/own",{
        method: 'GET',
        credentials: 'include', //if you dont set this include then you can't pass cookie
        headers: {
            Cookie: document.cookie
        }
    }).then(response=>{
        return response.text();
    }).then(res=>{
        allOwnPoemTable.style.display="block"
        //console.log(res);
        res=res.slice(res.indexOf("<Poem>"),res.lastIndexOf("</Poem>")+"</Poem>".length);
        //console.log(res);
        const poems=res.split(/\r?\n/);
        //console.log(poems)

        for(let i=0;i<poems.length;i++){
            //console.log(poems[i])
            let poem=extractXMLData(poems[i],'<Poem>','</Poem>');
            //console.log(poem);
            let row=allOwnPoemTable.insertRow(i+1);
            let cell1=row.insertCell(0);
            let cell2=row.insertCell(1);
            let cell3=row.insertCell(2);
            cell1.innerHTML=`${extractXMLData(poem,"<poemID>","</poemID>")}`
            cell2.innerHTML=`${extractXMLData(poem,"<poem>","</poem>")}`
            cell3.innerHTML=`${extractXMLData(poem,"<email>","</email>")}`
        
        }
        allOwnPoemTable.innerHTML+="<br>";
        //console.log(allOwnPoemTable.innerHTML)
    })
}

addPoem = ()=>{
    clearTableData()
    title = document.forms["add-poem"]["title"].value;
    document.forms["add-poem"].reset();
    //console.log(title);
    let data = `<poem><title>${title}</title></poem>`
    fetch('http://localhost:8180/poem', {
        method: 'POST',
        body: data,
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then( ()=> {
        alert("Poem added successfully!!");
    }).catch(e=>{
        console.log(e);
    })
}

editPoem = ()=>{
    clearTableData()
    id = document.forms["edit-poem"]["id"].value;
    title = document.forms["edit-poem"]["title"].value;
    document.forms["edit-poem"].reset();
    //console.log(title);
    //console.log(id);

    let data = `<poem><title>${title}</title></poem>`
    fetch(`http://localhost:8180/poem/${id}`, {
        method: 'PUT',
        body: data,
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then( (response)=> {
        return response.text();
    }).then(res=>{
        let msg=extractXMLData(res,'<message>','</message>');
        if(msg==="Poem updated")
            alert("Poem edited successfully!!");
        else
            alert("You can't edit this poem!!");
    

    })
    
}

deletePoem = ()=>{
    clearTableData()
    id = document.forms["delete-poem"]["id"].value;
    document.forms["delete-poem"].reset();
    //console.log(id)
    fetch(`http://localhost:8180/poem/${id}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then( (response)=> {
        return response.text();
    }).then(res=>{
        let msg=extractXMLData(res,'<message>','</message>');
        if(msg==="Poem deleted")
            alert("Poem deleted!!!");
        else
            alert("You can't delete this poem!!");
    

    })
}

deleteAllPoem = ()=>{
    clearTableData()
    fetch(`http://localhost:8180/deleteall`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            Cookie: document.cookie
        }
    }).then( ()=> {
        alert("All of your poems are deleted!!!")
    })
}

clearTableData = ()=>{
    poemIDTable.style.display="none"; //hiding the table 
    allPoemTable.style.display="none"; //hiding the table
    allOwnPoemTable.style.display="none";//hiding the table
    
}

extractXMLData = (str, parameter1, parameter2) => {
    let start = str.indexOf(parameter1) + parameter1.length //returns the last index of param1
    let end = str.indexOf(parameter2)//first index of param2
    return str.slice(start, end); //slicing the string between param1 and param2
}

disableButtons= (connectionStatus)=>{
    if(connectionStatus){
        loginBtn.disabled=false; //enable the button if the internet is ok
        logoutBtn.disabled=false;
        addPoemBtn.disabled=false;
        editPoemBtn.disabled=false;
        deletePoemBtn.disabled=false;
        deleteAllPoemBtn.disabled=false;
    }else{
        loginBtn.disabled=true; //disable the button if no internet connection
        logoutBtn.disabled=true;
        addPoemBtn.disabled=true;
        editPoemBtn.disabled=true;
        deletePoemBtn.disabled=true;
        deleteAllPoemBtn.disabled=true;
    }
}

