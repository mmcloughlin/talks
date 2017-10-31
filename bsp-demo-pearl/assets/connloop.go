cell, _ := c.ReceiveCell()
switch cell.Command() {
case CommandCreate, CommandCreate2:
	CreateHandler(c, cell)
case CommandCreated, CommandCreated2, CommandRelay, CommandRelayEarly, CommandDestroy:
	s, ok := c.circuits.Sender(cell.CircID()) // HL
	if !ok {
		bad()
	}
	s.SendCell(cell) // HL
case CommandPadding, CommandVpadding:
	logger.Debug("skipping padding cell")
default:
	logger.Error("no handler registered")
}

