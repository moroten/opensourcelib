
k2/version.py: Makefile
	@echo "# This file is automatically generated by Makefile" > k2/version.py
	@echo "__version__ = '${VERSION_STRING}$(UPGRADE_VERSION)'" >> k2/version.py
