#!/bin/sh

set -e

CUSTOM_REPO=$(dirname $(realpath $0))
INSTANCE_ROOT=$(dirname $(dirname $CUSTOM_REPO))
CUSTOM_ADDONS=$INSTANCE_ROOT/custom-addons
INSTANCE_USER=$(stat --format %U $INSTANCE_ROOT)
INSTANCE_DB=$INSTANCE_USER
INSTANCE_SERVICE=$INSTANCE_USER
INSTANCE_CONF=/etc/$INSTANCE_USER/main.conf

if [ ! -f "$INSTANCE_ROOT/libreerp/odoo-bin" ] || [ ! -f $INSTANCE_CONF ]; then
    echo failed to detect instance, exiting
    exit 1
fi

SU_USER=
if [ $(whoami) != $INSTANCE_USER ]; then
    SU_USER="sudo -u $INSTANCE_USER"
fi

$SU_USER sh <<HEREDOC
set -e
# configure git
git config --global user.email "\$USER@$(hostname)"
git config --global user.name "\$USER"
git config --global init.defaultBranch main
git config --global pull.rebase false

# update custom repo for newest repos.yml/requirements.txt
git -C $CUSTOM_REPO pull

# activate venv
. $INSTANCE_ROOT/venv/bin/activate
cd $CUSTOM_ADDONS

# aggregate code from oca repos
if [ -f $CUSTOM_REPO/repos.yml ]; then
    pip install -U git-aggregator
    gitaggregate -c $CUSTOM_REPO/repos.yml
fi

# link modules to custom-addons
for MANIFEST in \$(find $CUSTOM_ADDONS -name __manifest__.py); do
    ln -rsnf \$(dirname \$MANIFEST)
done
find $CUSTOM_ADDONS -maxdepth 1 -xtype l -delete

if [ -f $CUSTOM_REPO/requirements.txt ]; then
    pip install -Ur $CUSTOM_REPO/requirements.txt
fi

$INSTANCE_ROOT/libreerp/odoo-bin shell -d $INSTANCE_DB -c $INSTANCE_CONF <<ODOODOC
self.env['ir.module.module'].update_list()
auto_update = self.env['ir.module.module'].search([('name', '=', 'module_auto_update')])
if not auto_update:
    print('Unable to install module_auto_update')
else:
    if auto_update.state != 'installed':
        auto_update.button_immediate_install()
    self.env['ir.module.module'].upgrade_changed_checksum()
ODOODOC

HEREDOC

sudo systemctl restart $INSTANCE_SERVICE
