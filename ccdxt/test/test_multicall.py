from ccdxt.base.multicall import Multicall

mc = Multicall('klaytn')
mc.addCall('0x2b5065d6049099295c68f5fcb97b8b0d3c354df7', 'symbol')
mc.addCall('0x2b5065d6049099295c68f5fcb97b8b0d3c354df7', 'name')
mc.addCall('0x2b5065d6049099295c68f5fcb97b8b0d3c354df7', 'decimals')
mc.execte
data = mc.execute()

# print results
itemsPerLine = 4
itemCount = 0
first = True
allLines = []
line = []
for element in data:
	if itemCount % itemsPerLine == 0 and not first:
		allLines.append("\t".join(line))
		line = []

	for subelement in element:
		line.append(str(subelement))
	itemCount += 1
	first = False

print()
print("\tSYM\tName\t\tDec\tAmount in Balancer Vault (wei)")
print("\t---\t----\t\t---\t------------------------------")
for line in allLines:
	print("\t" + line)
print()