//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];


class Node
{
	constructor(parent)
	{
		this.parent = parent;
		this.children = [];
		this.actions = [];
		this.score = null;
		this.state = null;
	}
	
	addChild(child)
	{
		this.children.push(child);
	}
	
	removeChild(child)
	{
		this.children.remove(child);
	}
	
	setScore(newScore)
	{
		this.score = newScore;
	}
	
	setState(newState)
	{
		this.state = newState;
	}
	
	setActions(actions)
	{
		this.actions = actions;
	}
	
	getBestChild()
	{
		let best_score = -9001;
		let best_child = null;
		for (const child of this.children)
		{
			if(child.score > best_score)
			{
				best_score = child.score;
				best_child = child;
			}
		}
		
		return best_child;
	}	
}

var decisionSpace;
//INIT::::
// Set Feature space to empty (FS)
// Set the start state as the root of the search tree (DS)
// Assign a weight of zero to the root state (DS)
// Add feature values to the root state (DS)
// Project root state onto a cell in feature space (FS)
// Assign weights to all moves from the root state (DS + FS)


//SEARCH::::
//while no solution has been found
// Pick the next cell in feature space (FS)
// Find all search-tree states that project onto this cell (DS)
// Identify all un-expanded moves from these states (DS)
// Choose move with least accumulated weight (DS)
// Add the resulting state to the search tree (DS)
// Added state's weight = parent's weight + move weight (DS)
// Add feature values to the added state (DS)
// Project added state onto a cell in feature space (FS)
// Assign weights to all moves from the added state (DS + FS)
var solutionFound = false;
var actionSet = [];

// possible features for the FS:
// 1. Number of Goals unlocked
// 2. Number of Players
// 3. Connectivity
// 3.1. Room Connectivity? 
// 4. Out of Plan
// 5. Elim of Threats (Count the killables)
// 6. Closest MHDistance of Player Objects to Winnable Object
// 7. Distance to threats 

// Heuristics for FS 

// 1. Number Of Goals unlocked
function nbrOfGoals(state, weight=1) {
	return (weight * state.winnables.length);
}
// 2. Number of Players
function nbrOfPlayers(state, weight=1) {
	return (weight * state.players.length);
}
// 3. Connectivity
function connectivity(state, weight=1) {
	mapRes = {Map: parseRoomForConnectivityFeature(state)}; 
	var currentRooms = 0;
	var mapL = mapRes.Map.length;
	for(var i = 0; i < mapL ; i++) 
	{
		var row = mapRes.Map[i];
		var rowL = row.length;
		for(var j = 0; j < rowL; j++) 
		{
			if(mapRes.Map[i][j] === '0')
			{
				currentRooms++;
				_connectivity(mapRes, i, j, mapL, rowL);
			}
		}	
	}
	
	return  (weight * -currentRooms); // turns minimizing into maximizing
}

//4. Out of plan - Sums the unusable words
function outOfPlan(state, weight=1) {
	words = state.words
	for(var i=0; i < words.length; i++)
	{
		
	}
}

//5. Elim of Threats 
function elimOfThreats(state, weight=1)
{
	return weight * state.killers.length;
}

//6. avg Distance to winnable, words and pushable
function distanceHeuristic(state, weight=1)
{
	if(state['players'].length == 0)
	{
		return -50; 
	}
	else 
	{
		let win_d = heuristic2(state['players'], state['winnables']);
		let word_d = heuristic2(state['players'], state['words']);
		let push_d = heuristic2(state['players'], state['pushables']);
		return (weight * -((win_d+word_d+push_d)/3));
	}
}

// 7. avg distance to killables
function distanceToKillables(state, weight=1)
{
	let kill_d = heuristic2(state['players'], state['killers']);
	return (weight * kill_d);
}

function _connectivity(map, i, j, mapL, rowL) {
	map.Map[i][j] = '1';
	
	if((i+1) < mapL) {
		if(map.Map[i+1][j] === '0')
		{
			_connectivity(map, i+1, j, mapL, rowL);
		}
	}
	if((i-1) >= 0) {
		if(map.Map[i-1][j] === '0')
		{
			_connectivity(map, i-1, j, mapL, rowL);
		}
	}
	if((j+1) < rowL) {
		if(map.Map[i][j+1] === '0')
		{
			_connectivity(map, i, j+1, mapL, rowL);
		}
	}
	if((j-1) >= 0) {
		if(map.Map[i][j-1] === '0')
		{
			_connectivity(map, i, j-1, mapL, rowL);
		}
	}
}

// What advisors/recommended moves do we need? 
// Advisors assign small weights to moves that the recommended
// and a larger weights for the ones they do not
// Ensures that theese moves are considered first before any other
// Stop as soon as goal is reached an return the action set

function parseRoomForConnectivityFeature(state) 
{
	map = state.orig_map;
	map_cp = JSON.parse(JSON.stringify(map))
	for(let i = 0; i < map.length; i++)
	{
		let row = map[i];
		for(let j = 0; j < row.length; j++)
		{
			let str = map[i][j];
			if(str === ' ') {
				str = '0';
			}
			else {
				str = '1';
			}
			map_cp[i][j] = str;
		}
	}
	
	// Don't count players as blocking room, otherwise moving
	// inbetween bottlenecks/tunnels would reduce the FS score
	players = state.players
	for(let i = 0; i < players.length; i++)
	{
		let player = players[i];
		map_cp[player.y][player.x] = '0';
	}
	
	return map_cp
	
}

// FIND AVERAGE DISTANCE OF GROUP THAT IS CLOSEST TO ANOTHER OBJECT IN A DIFFERENT GROUP
function heuristic2(g1, g2){
	let allD = [];
	for(let g=0;g<g1.length;g++){
		for(let h=0;h<g2.length;h++){
			let d = dist(g1[g], g2[h]);
			allD.push(d);
		}
	}

	let avg = 0;
	for(let i=0;i<allD.length;i++){
		avg += allD[i];
	}
	if(allD.length>0){
		return avg/allD.length;
	}
	else 
	{
		return 0;
	}
}

// BASIC EUCLIDEAN DISTANCE FUNCTION FROM OBJECT A TO OBJECT B
function dist(a,b){
	return (Math.abs(b.x-a.x)+Math.abs(b.y-a.y));
}

// All Features are called here, so this place could be edited
// for grid search of importance of features
function callAllFeaturesAndSum(state)
{
	let score = 0;
	score += nbrOfGoals(state);
	score += nbrOfPlayers(state);
	score += connectivity(state);
	score += elimOfThreats(state);
	score += distanceHeuristic(state);
	score += distanceToKillables(state);
	return score;
}

function newState(kekeState, map) 
{
	simjs.clearLevel(kekeState);
	kekeState.orig_map = map;
	[kekeState.back_map, kekeState.obj_map] = simjs.splitMap(kekeState.orig_map);
	simjs.assignMapObjs(kekeState);
	simjs.interpretRules(kekeState);
}

var penis = 0;
// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	// PERFORM ITERATIVE CALCULATIONS HERE //
	
	var vadda = decisionSpace;
	var iteration = 0
	while (!solutionFound)
	{
		// Instead of looking at all options we could use advisors
		// as written in the FESS paper
		
		let state = vadda.state;
		iteration++;
		
		for (var action = 0; action < possActions.length; action++)
		{
			let actionTaken = possActions[action];
			let res = simjs.nextMove(actionTaken, state);
			let new_state = res['next_state'];
			newState(new_state, simjs.parseMap(simjs.showState(new_state)))
			let resultActions = JSON.parse(JSON.stringify(vadda.actions))
			resultActions.push(actionTaken);
			
			if(res['won'])
			{
				console.log(iteration);
				console.log('I got you fam!');
				solutionFound = true;
				return resultActions;
			}
			
			let score = callAllFeaturesAndSum(new_state);
			let childNode = new Node(vadda);
			childNode.setScore(score);
			childNode.setActions(resultActions);
			childNode.setState(new_state);
			if(penis<2){
				console.log(simjs.parseMap(simjs.showState(vadda.state)));
				penis++;
			}
			vadda.addChild(childNode);
		}
		
		let best_child = vadda.getBestChild();
		vadda = best_child;
	}
	//if(notsent) {
		//console.log(connectivity(init_state));
		//console.log(simjs.map2Str(init_state.obj_map));
		//console.log(init_state.players[0]);
		//notsent = false;
		//let new_state = simjs.nextMove("right", init_state);
		//console.log(simjs.map2Str(new_state['next_state'].obj_map));
		//console.log(new_state['next_state'].players[0]);
	//}
	
	//return a sequence of actions or empty list
	return [];
}

function init(init_state) {
	decisionSpace = new Node(null);
	decisionSpace.setState(init_state);
	decisionSpace.setScore(0);
	solutionFound = false;
}

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){init(init_state);},							// initializing function here
	best_sol : function(){return [];}				//returns closest solution in case of timeout
}


