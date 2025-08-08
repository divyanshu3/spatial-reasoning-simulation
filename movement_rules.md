Boundary Check: Objects inside the grid cannot cross the boundary; attempting to do so results in an invalid step/movement.

Single Mobile Agent: Only the designated mobile object (typically a "Person") can take a step; other objects remain static.

Collision Detection: If a destination cell for a move is already occupied by another (immovable) object, the step is invalid.

Completion of Steps: A total number of steps (and/or rotations) allowed/specified for a scenario will be given, and the mobile object is intended to attempt or complete all specified actions in the sequence. 4a. Final Destination Check for Compound Translational Moves: If a scenario specifies a single block of translational movement intended to reach a 'final destination' (e.g., 'move X steps in direction Y'): a. The system will first calculate the final target (x,y) coordinates that would result from completing all specified translational steps in that block. b. Only this calculated final destination cell is then checked for validity against Rule 1 (Boundary Check) and Rule 3 (Occupancy Check). c. If this final destination cell is invalid, the entire compound movement block is considered invalid, and the mobile object does not move from its position before attempting this compound move. Its orientation also remains unchanged. d. If the final destination cell is valid, the mobile object moves directly to this final cell. Intermediate cells traversed during this compound move are effectively 'passed through' or 'jumped over' without individual validity checks for occupancy or boundaries during this specific compound move.

Defined Movement Actions: The allowed movement actions (e.g., relative directions like "front," "left," "right," "behind," or specific rotations) will be provided for the mobile object, typically as part of a scenario's action sequence.

Initial Orientation: The initial facing direction (e.g., North, South, East, West) of the mobile object will be given at the start of a scenario.

In-Place Rotation Capability: Mobile objects can rotate (change orientation) within the same grid cell if an instruction for rotation is given.

Definition of a "Step" (Single Translational Movement): A "step" constitutes a translational movement by the mobile object to an immediately adjacent grid cell. Steps are not diagonal and are defined by relative directions (e.g., "front," "behind," "left," "right") based on the object's current orientation.

Definition of "Rotation" (Orientation Change): A "rotation" changes the mobile object's facing orientation (e.g., from North to East) but does not change its (x,y) grid cell position. Allowed rotations will be specified by instructions (e.g., "turn left 90 degrees," "turn right 90 degrees," "turn around 180 degrees").

Consequence of an Invalid Single Step: If an attempted individual translational step (as defined in Rule 8, and not part of a compound move governed by Rule 4a) is deemed invalid (due to Rule 1: Boundary Check, or Rule 3: Occupancy Check), the mobile object does not move from its current cell for that attempted step, and its orientation remains unchanged by that attempt.

Nature of Action Sequences: A movement scenario will typically consist of a predefined sequence of actions. Each action in the sequence will be either an individual "step" (Rule 8), a "rotation" (Rule 9), or a compound translational move (Rule 4a), to be performed by the designated mobile object.

State Updates After Valid Discrete Actions: After each successfully completed and valid discrete action (an individual step as per Rule 8/10, a rotation as per Rule 9, or a whole compound move successfully validated by Rule 4a), the mobile object's state (its position (x,y) for a step/compound move, or its facing orientation for a rotation) within the grid is considered immediately updated before any subsequent action in the sequence is evaluated or performed.

Single Mobile Agent per Scenario: For any given generated scenario involving movement, there will be only one designated object acting as the active mobile agent performing the sequence of actions.

Orientation Preservation During Translational Steps: When a mobile object successfully completes a translational "step" (moving front, behind, left, or right as per Rule 8), its facing orientation is preserved and does not change as a result of that step. Orientation changes only occur via explicit "rotation" actions (Rule 7 and Rule 9).
