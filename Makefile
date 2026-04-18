.PHONY: cleangit

cleangit:
	git rm --cached -rf .idea/
	git commit -m "Usuń .idea ze śledzenia git"
