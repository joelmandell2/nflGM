import { useEffect, useState } from 'react';
import { Container, Divider, Link } from '@mui/material';
import PlayerCard from '../components/PlayerCard'


import LazyTable from '../components/lazytable';
const config = require('../config.json');


// export means other functions can use it
// default means it is the main export of the file
// don't need to pass in curly braces
export default function HomePage () {
    // states you're gonna need: 
    // year for draft class
    // position
    
    // use state returns both the variable value a function to set it in the future
    const [draftYear, setDraftYear] = useState(2025);
    const [position, setPosition] = useState('WR');
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [selectedAttrib, setSelectedAttrib] = useState('classification');


    // use effect is a function that takes in the definition of another funciton
    // that function is then executed 
    // called whenever the page loads
    useEffect( () => {
        // returns a promise for an object (basically like saying that object will be there in the future)
        // then is called on that object once it is returned
        console.log('about to fetch from :', config.server_host, config.server_port);
        fetch(`http://${config.server_host}:${config.server_port}/player?year=${draftYear}&position=${position}&sort=${selectedAttrib}`)
        .then(res => res.json())
        .then(resJson => {
                // the map function applies whatever you tell it to do to each value element in array you're calling it on (resJson)
                // player is the element in the array that is being iterated over
                // sets current player to playerData
                console.log('Fetched draft year response:', resJson); // Log to debug
                // Check if resJson is an array, otherwise look for players property
                const dataArray = Array.isArray(resJson) ? resJson : resJson.players || [];
                const playerData = dataArray.map((player) => {
                    return ({id: player.player_id || Math.random(), ...player});
                });
                setSelectedPlayer(playerData);
        })
        

    }, [position, draftYear, selectedAttrib]);


    // field is the name of the attribute you get from the database
    // headername is what it's called outside
    const playerColumns = [
        {
            field: 'name',
            headerName: 'Player',
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Weight}
            // </div>
        },
        {
            field: 'Height',
            headerName: 'Height',
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Weight}
            // </div>
        },
        {
            field: 'Weight',
            headerName: 'Weight',
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Weight}
            // </div>
        },
        {
            field: 'Forty',
            headerName: '40 Yard Dash'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Forty}
            // </div>
        },
        {
            field: 'Shuttle',
            headerName: 'Shuttle'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Shuttle}
            // </div>
        },
        {
            field: 'Cone',
            headerName: '3 Cone'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Cone}
            // </div>
        },
        {
            field: 'Broad',
            headerName: 'Broad Jump'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Broad}
            // </div>
        },
        {
            field: 'Bench',
            headerName: 'Bench Press'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('name')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Bench}
            // </div>
        },
        {
            field: 'Vertical',
            headerName: 'Vertical'
            // ,
            // renderCell: (row) => <div onClick={ () => setSelectedPlayer('Vertical')}
            // style={{ cursor: "pointer", color: "white"}}>
            //     {row.Vertical}
            // </div>
        },
        
        

    ];

    // the html that the page actually returns
    // probably need to fix lazy table route


    return(
        <Container>
            {/* {selectedPlayer && <PlayerCard playerName={selectedPlayer} year={draftYear} pos={position}/>} */}
            <Divider />
            <LazyTable route={`http://${config.server_host}:${config.server_port}/player?year=${draftYear}&position=${position}&sort=${selectedAttrib}`} columns={playerColumns} onYearChange={setDraftYear} onPositionChange={setPosition} onSelectedChange={setSelectedAttrib}/>
            <Divider />
        </Container>
    );

};