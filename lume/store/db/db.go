package db

import (
	"github.com/pkg/errors"

	"github.com/Rheinmir/lume/internal/profile"
	"github.com/Rheinmir/lume/store"
	"github.com/Rheinmir/lume/store/db/mysql"
	"github.com/Rheinmir/lume/store/db/postgres"
	"github.com/Rheinmir/lume/store/db/sqlite"
)

// NewDBDriver creates new db driver based on profile.
func NewDBDriver(profile *profile.Profile) (store.Driver, error) {
	var driver store.Driver
	var err error

	switch profile.Driver {
	case "sqlite":
		driver, err = sqlite.NewDB(profile)
	case "mysql":
		driver, err = mysql.NewDB(profile)
	case "postgres":
		driver, err = postgres.NewDB(profile)
	default:
		return nil, errors.New("unknown db driver")
	}
	if err != nil {
		return nil, errors.Wrap(err, "failed to create db driver")
	}
	return driver, nil
}
