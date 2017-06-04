

autor=xbenom01
SOURCES= antipirat Utility.py TRKparse.py TORparse.py RSSparse.py README Makefile manual.pdf test_files
LIBS= bencode.py BTL.py

all:
	chmod +x antipirat

test:
	@echo "TEST1" 
	./antipirat -i test_files/example.xml
	@echo "" 

	@echo "TEST2" 
	./antipirat -i test_files/peers.xml
	@echo "" 
	
	@echo "TEST3" 
	./antipirat -i test_files/unregistered.xml
	@echo "" 

pack:
	cp doc/manual.pdf .
	tar cvzf $(autor).tgz $(SOURCES) $(LIBS)

remove:
	rm -f *.peerlist
